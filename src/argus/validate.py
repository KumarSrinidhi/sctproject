"""Validation rules.

Fixes audit finding D1: in the legacy pipeline a row that failed validation was
*logged* as rejected and then appended anyway. Here any `error` blocks
`argus build` unless that row carries an explicit, reviewed waiver for that rule.

Each rule has a stable id so waivers and reports can refer to it.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import math
import re
from collections import defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Callable, Iterable, Literal

from .schema import CONFIDENCE_LEVELS, VALUE_SOURCES, Measurement, PaperRecord
from .units import k_unit_factor

Severity = Literal["error", "warning"]


@dataclass(frozen=True)
class Rule:
    id: str
    severity: Severity
    description: str


@dataclass
class Issue:
    rule: str
    severity: Severity
    paper_id: str
    row_id: str
    message: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


RULES: dict[str, Rule] = {r.id: r for r in [
    # --- structure / identity ---
    Rule("doi_format", "error", "DOI looks like 10.NNNN/suffix."),
    Rule("paper_id_format", "error", "paper_id is P followed by digits."),
    Rule("year_range", "error", "Publication year is plausible."),
    Rule("row_id_format", "error", "row_id is md5(doi)[:8]-NNN for this paper's DOI."),
    Rule("row_id_unique", "error", "row_id is unique across the dataset."),
    Rule("tombstone_reused", "error", "A deliberately removed row_id (data/tombstones.yaml) does not reappear."),
    Rule("duplicate_measurement", "error", "No two rows describe the same sample, condition and value."),
    # --- the measured value ---
    Rule("k_present_positive", "error", "k_composite_W_mK is a positive number."),
    Rule("k_unit_known", "error", "k_original_unit is a recognised conductivity unit."),
    Rule("k_normalized_consistent", "error", "k_composite_W_mK equals k_original_value converted to W/(m K)."),
    Rule("k_plausible", "warning", "k_composite_W_mK within 0.05-100 W/(m K) for a polymer composite."),
    Rule("k_above_matrix", "warning", "Composite k is not below the neat-matrix k."),
    # --- composition ---
    Rule("loading_present", "error", "At least one of vol%, wt% or the original loading value is given."),
    Rule("loading_range", "error", "vol% and wt% lie in [0, 100]."),
    Rule("hybrid_label", "warning", "Multi-filler labels (a/b, a+b) contain 'hybrid' (README convention)."),
    Rule("loading_basis_consistent", "warning",
         "When both wt% and vol% are given for a single filler, they agree (within 5 vol%) under reference densities."),
    # --- provenance policy ---
    Rule("source_location_present", "error", "source_location says where in the paper the value is."),
    Rule("value_source_vocab", "error", "value_source is text | table | figure."),
    Rule("confidence_vocab", "error", "confidence is High | Medium | Low."),
    Rule("figure_not_high", "error", "Figure-digitized values are never High confidence."),
    Rule("abstract_not_high", "error", "Abstract-only values are never High confidence."),
]}

_DOI = re.compile(r"^10\.\d{4,9}/\S+$")
_ROW_ID = re.compile(r"^(?P<h>[0-9a-f]{8})-(?P<n>\d{3,})$")
_PAPER_ID = re.compile(r"^P\d{3,}$")

# Fields that together identify "the same sample measured under the same condition".
IDENTITY_FIELDS = (
    "matrix_polymer", "curing_agent", "filler_material", "filler_shape", "filler_mean_size_um",
    "filler_loading_vol_pct", "filler_loading_wt_pct", "filler_loading_original_value",
    "functionalization", "filler_alignment", "processing_method", "k_direction",
    "measurement_temperature_C", "k_composite_W_mK",
)


_ABSTRACT_ONLY = re.compile(r"^\s*abstract\s*\(", re.IGNORECASE)


def is_abstract_only(source_location: str | None) -> bool:
    """README convention: values taken from an abstract alone (no full text) are
    prefixed 'Abstract (...)'. 'Abstract + Results: ...' is a full-text quote."""
    return bool(_ABSTRACT_ONLY.match(source_location or ""))


LOADING_TOLERANCE_VOL_PCT = 5.0


def _converted_vol(m: Measurement, wt: float) -> float | None:
    from .units import wt_to_vol
    from .vocab import classify_filler, classify_matrix, filler_props, matrix_prefilled, matrix_props

    fil = classify_filler(m.filler_material)
    if fil.is_hybrid or not fil.base or matrix_prefilled(m.matrix_polymer):
        return None
    fp, mp = filler_props(fil.base), matrix_props(classify_matrix(m.matrix_polymer))
    if fp is None or mp is None:
        return None
    return wt_to_vol(wt, fp["density"], mp["density"])


def doi_hash(doi: str) -> str:
    return hashlib.md5((doi or "nodoi").encode()).hexdigest()[:8]


def measurement_key(doi: str, m: Measurement) -> tuple:
    return (doi.lower(),) + tuple(getattr(m, f) for f in IDENTITY_FIELDS)


def _num(v: Any) -> float | None:
    if isinstance(v, bool) or v is None:
        return None
    if isinstance(v, (int, float)) and math.isfinite(v):
        return float(v)
    return None


class _Collector:
    def __init__(self) -> None:
        self.issues: list[Issue] = []

    def add(self, rule_id: str, rec: PaperRecord, m: Measurement | None, msg: str) -> None:
        rule = RULES[rule_id]
        if m is not None and any(w.rule == rule_id for w in m.waivers):
            return
        self.issues.append(Issue(rule_id, rule.severity, rec.paper_id, m.row_id if m else "", msg))


def _check_paper(c: _Collector, rec: PaperRecord) -> None:
    if not _PAPER_ID.match(rec.paper_id):
        c.add("paper_id_format", rec, None, f"bad paper_id {rec.paper_id!r}")
    if not _DOI.match(rec.paper.doi or ""):
        c.add("doi_format", rec, None, f"bad DOI {rec.paper.doi!r}")
    this_year = _dt.date.today().year
    if rec.paper.year is None or not 1900 <= rec.paper.year <= this_year + 1:
        c.add("year_range", rec, None, f"year {rec.paper.year!r}")


def _check_measurement(c: _Collector, rec: PaperRecord, m: Measurement) -> None:
    add: Callable[[str, str], None] = lambda rule, msg: c.add(rule, rec, m, msg)  # noqa: E731

    mm = _ROW_ID.match(m.row_id)
    if not mm:
        add("row_id_format", f"bad row_id {m.row_id!r}")
    elif mm.group("h") != doi_hash(rec.paper.doi):
        add("row_id_format", f"row_id prefix {mm.group('h')} != md5(doi)[:8] {doi_hash(rec.paper.doi)}")

    # value
    k = _num(m.k_composite_W_mK)
    if k is None or k <= 0:
        add("k_present_positive", f"k_composite_W_mK={m.k_composite_W_mK!r}")
    factor = k_unit_factor(m.k_original_unit or "")
    if factor is None:
        add("k_unit_known", f"unrecognised unit {m.k_original_unit!r}")
    ko = _num(m.k_original_value)
    if k is not None and factor is not None:
        if ko is None:
            add("k_normalized_consistent", "k_original_value missing")
        elif not math.isclose(ko * factor, k, rel_tol=1e-6, abs_tol=1e-9):
            add("k_normalized_consistent", f"{ko} {m.k_original_unit} -> {ko * factor:g} W/(m K), row says {k}")
    if k is not None and k > 0 and not 0.05 <= k <= 100:
        add("k_plausible", f"k={k}")
    km = _num(m.k_matrix_W_mK)
    if k is not None and km is not None and k < km:
        add("k_above_matrix", f"k={k} < k_matrix={km}")

    # composition
    vol, wt = _num(m.filler_loading_vol_pct), _num(m.filler_loading_wt_pct)
    orig = m.filler_loading_original_value
    if vol is None and wt is None and orig in (None, ""):
        add("loading_present", "no vol%, wt% or original loading value")
    for name, v in (("vol%", vol), ("wt%", wt)):
        if v is not None and not 0 <= v <= 100:
            add("loading_range", f"{name}={v}")
    fm = m.filler_material or ""
    if re.search(r"[/+]", fm) and "hybrid" not in fm.lower():
        add("hybrid_label", f"filler_material={fm!r}")
    if vol is not None and wt is not None and 0 < wt < 100:
        conv = _converted_vol(m, wt)
        if conv is not None and abs(conv - vol) > LOADING_TOLERANCE_VOL_PCT:
            add("loading_basis_consistent",
                f"{wt} wt% -> {conv:.1f} vol% with reference densities, but row says {vol} vol% "
                "(is wt% a formulation designation rather than the composite mass fraction?)")

    # provenance policy
    if not (m.source_location or "").strip():
        add("source_location_present", "empty source_location")
    if m.value_source not in VALUE_SOURCES:
        add("value_source_vocab", f"value_source={m.value_source!r}")
    if m.confidence not in CONFIDENCE_LEVELS:
        add("confidence_vocab", f"confidence={m.confidence!r}")
    if m.value_source == "figure" and m.confidence == "High":
        add("figure_not_high", "figure-derived value marked High")
    if is_abstract_only(m.source_location) and m.confidence == "High":
        add("abstract_not_high", "abstract-only value marked High")


def validate_records(records: Iterable[PaperRecord], tombstones: Iterable[str] = ()) -> list[Issue]:
    """Run every rule over every record and return all issues found."""
    c = _Collector()
    records = list(records)
    dead = set(tombstones)
    seen_ids: dict[str, str] = {}
    keys: dict[tuple, list[tuple[PaperRecord, Measurement]]] = defaultdict(list)
    for rec in records:
        _check_paper(c, rec)
        for m in rec.measurements:
            _check_measurement(c, rec, m)
            if m.row_id in dead:
                c.add("tombstone_reused", rec, m, "row_id was removed earlier; see data/tombstones.yaml")
            if m.row_id in seen_ids:
                c.add("row_id_unique", rec, m, f"row_id also used in {seen_ids[m.row_id]}")
            else:
                seen_ids[m.row_id] = rec.paper_id
            keys[measurement_key(rec.paper.doi, m)].append((rec, m))
    for group in keys.values():
        if len(group) > 1:
            first = group[0][1].row_id
            for rec, m in group[1:]:
                c.add("duplicate_measurement", rec, m, f"same sample/condition/value as {first}")
    return c.issues


def summarize(issues: list[Issue]) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for i in issues:
        out[f"{i.severity}:{i.rule}"] += 1
    return dict(sorted(out.items()))


def errors(issues: list[Issue]) -> list[Issue]:
    return [i for i in issues if i.severity == "error"]
