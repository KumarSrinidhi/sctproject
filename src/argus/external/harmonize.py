"""Map external measurements onto the ARGUS row, then reuse ARGUS enrichment.

Each source adapter yields `ExternalRecord`s with the source's own wording. This
module normalises filler names, builds a 31-column ARGUS row and runs the same
`enrich_row` the curated dataset uses, so wt%->vol% conversion, method classes,
direction rules and flags are identical on both sides.
"""
from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass, field
from typing import Any, Iterable

from ..enrich import enrich_row
from ..schema import COLUMN_NAMES

# raw filler wording -> ARGUS filler label (order matters: specific before generic)
_FILLER_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("BNNS", re.compile(r"\bBNNS\b|BN\s*nano\s*sheets?|boron\s*nitride\s*nano\s*sheets?|\bBNNSs\b|exfoliated\s*(?:h-?)?BN", re.I)),
    ("cBN", re.compile(r"\bc-?BN\b|cubic\s*boron\s*nitride", re.I)),
    ("h-BN", re.compile(r"\bh-?BN\b|hexagonal\s*boron\s*nitride", re.I)),
    ("BN", re.compile(r"\bBN\b|boron\s*nitride", re.I)),
    ("AlN", re.compile(r"\bAlN\b|alumin(?:i)?um\s*nitride", re.I)),
    ("Al2O3", re.compile(r"\bAl2O3\b|al₂o₃|alumina|alumin(?:i)?um\s*oxide", re.I)),
    ("MgO", re.compile(r"\bMgO\b|magnesi(?:a|um\s*oxide)", re.I)),
    ("Si3N4", re.compile(r"\bSi3N4\b|silicon\s*nitride", re.I)),
    ("SiC", re.compile(r"\bSiC\b|silicon\s*carbide", re.I)),
    ("ZnO", re.compile(r"\bZnO\b|zinc\s*oxide", re.I)),
    ("SiO2", re.compile(r"\bSiO2\b|silica|fused\s*quartz", re.I)),
    ("glass", re.compile(r"\bglass\b(?!\s*fib)", re.I)),
    ("diamond", re.compile(r"diamond", re.I)),
    ("graphene", re.compile(r"graphene|\bGNPs?\b|\brGO\b|graphene\s*oxide", re.I)),
    ("CNT", re.compile(r"\bCNTs?\b|\bMWCNTs?\b|\bSWCNTs?\b|carbon\s*nano\s*tubes?", re.I)),
    ("graphite", re.compile(r"graphite", re.I)),
    ("carbon fiber", re.compile(r"carbon\s*fib(?:er|re)", re.I)),
    ("Cu", re.compile(r"\bCu\b|copper", re.I)),
    ("Ag", re.compile(r"\bAg\b|silver", re.I)),
    ("Al", re.compile(r"\bAl\b|alumin(?:i)?um(?!\s*(?:nitride|oxide))", re.I)),
]
_SPLIT = re.compile(r"\s*(?:\+|/|&|,|;|\band\b)\s*", re.I)
CARBON = frozenset({"graphene", "CNT", "graphite", "carbon fiber"})
METAL = frozenset({"Cu", "Ag", "Al"})


def normalize_filler(raw: str | None) -> str:
    """ARGUS filler label: one base label, '<a>/<b> hybrid', 'none', or the raw text if unknown."""
    s = (raw or "").strip()
    if not s or s.lower() in ("none", "neat", "pure", "unfilled", "-"):
        return "none"
    parts = [p for p in _SPLIT.split(s) if p.strip()]
    labels: list[str] = []
    for p in parts or [s]:
        lab = next((name for name, rx in _FILLER_RULES if rx.search(p)), None)
        if lab and lab not in labels:
            labels.append(lab)
    if not labels:
        return s
    # 'BN' next to a more specific BN label is the same filler written twice
    if "BN" in labels and any(x in labels for x in ("h-BN", "BNNS", "cBN")):
        labels.remove("BN")
    return labels[0] if len(labels) == 1 else "/".join(labels) + " hybrid"


def normalize_doi(doi: str | None) -> str:
    d = (doi or "").strip().lower()
    d = re.sub(r"^(?:https?://)?(?:dx\.)?doi\.org/|^doi:\s*", "", d)
    return d.rstrip(".")


def _num(v: Any) -> float | None:
    if v is None or isinstance(v, bool):
        return None
    try:
        x = float(str(v).strip().replace(",", ".")) if isinstance(v, str) else float(v)
    except ValueError:
        return None
    return x if math.isfinite(x) else None


@dataclass
class ExternalRecord:
    """One measured k from an external source, in that source's own words."""
    source: str           # dataset key, e.g. 'zenodo_1234'
    ext_id: str           # row id inside the source
    k: float              # composite k, W/(m K)
    filler: str           # raw filler name
    matrix: str           # raw matrix name
    doi: str = ""
    vol_pct: float | None = None
    wt_pct: float | None = None
    k_matrix: float | None = None
    method: str = ""
    direction: str = ""
    size_um: float | None = None
    shape: str = ""
    treatment: str = ""
    alignment: str = ""
    processing: str = ""
    year: int | None = None
    temperature_C: float | None = None
    title: str = ""
    notes: str = ""
    group: str = ""       # paper grouping key when the DOI is a compilation of several papers
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def paper_key(self) -> str:
        """Grouping key for paper-level validation: explicit group, else DOI, else source + title."""
        if self.group:
            return f"{self.source}:{self.group}"
        d = normalize_doi(self.doi)
        return d or f"{self.source}:{(self.title or self.ext_id).strip().lower()}"


def paper_id(rec: ExternalRecord) -> str:
    return "X" + hashlib.md5(rec.paper_key.encode("utf-8")).hexdigest()[:7]


def to_row(rec: ExternalRecord) -> dict[str, Any]:
    """The 31-column ARGUS row for an external record (confidence 'External')."""
    doi = normalize_doi(rec.doi)
    vol, wt = _num(rec.vol_pct), _num(rec.wt_pct)
    row: dict[str, Any] = dict.fromkeys(COLUMN_NAMES, "")
    row.update(
        row_id=f"{rec.source}-{rec.ext_id}",
        doi=doi,
        source_url=f"https://doi.org/{doi}" if doi else "",
        paper_title=rec.title,
        year=rec.year if rec.year else "",
        matrix_polymer=rec.matrix,
        filler_material=normalize_filler(rec.filler),
        filler_material_original=rec.filler,
        filler_shape=rec.shape,
        filler_mean_size_um=_num(rec.size_um) if _num(rec.size_um) is not None else "",
        filler_loading_vol_pct=vol if vol is not None else "",
        filler_loading_wt_pct=wt if wt is not None else "",
        filler_loading_original_value=str(vol if vol is not None else wt if wt is not None else ""),
        filler_loading_original_unit="vol%" if vol is not None else "wt%" if wt is not None else "",
        functionalization=rec.treatment,
        filler_alignment=rec.alignment,
        processing_method=rec.processing,
        k_matrix_W_mK=_num(rec.k_matrix) if _num(rec.k_matrix) is not None else "",
        k_composite_W_mK=float(rec.k),
        k_direction=rec.direction,
        measurement_method=rec.method,
        measurement_temperature_C=_num(rec.temperature_C) if _num(rec.temperature_C) is not None else "",
        k_original_value=float(rec.k),
        k_original_unit="W/(m K)",
        value_source="external",
        source_location=f"external dataset {rec.source}, row {rec.ext_id}",
        confidence="External",
        notes=rec.notes,
    )
    return row


def enrich_external(records: Iterable[ExternalRecord]) -> list[dict[str, Any]]:
    """Enriched ARGUS-style rows (same derived columns) plus `ext_source` and `paper_key`."""
    out = []
    for rec in records:
        r = enrich_row(to_row(rec), paper_id(rec))
        r["ext_source"] = rec.source
        r["paper_key"] = rec.paper_key
        r["filler_class"] = filler_class(r["filler_material"])
        out.append(r)
    return out


def filler_class(label: str) -> str:
    """ceramic | carbon | metal | hybrid | none | unknown, for coverage tables."""
    if label == "none":
        return "none"
    if label.endswith(" hybrid"):
        return "hybrid"
    if label in CARBON:
        return "carbon"
    if label in METAL:
        return "metal"
    known = {name for name, _ in _FILLER_RULES}
    return "ceramic" if label in known else "unknown"
