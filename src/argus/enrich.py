"""Analysis-ready table: the 31 published columns plus derived, labelled columns.

Rule: enrichment never edits a record. Every derived value has a companion
`*_basis` column saying whether it was reported, converted, or a default, so a
reader can always separate what the paper printed from what we inferred.
"""
from __future__ import annotations

import math
import statistics
from collections import Counter
from dataclasses import dataclass
from typing import Any

from .io import csv_bytes
from .schema import COLUMN_NAMES, PaperRecord, measurement_to_row
from .units import vol_to_wt, wt_to_vol
from .validate import is_abstract_only
from .vocab import (
    PLATELET_BN,
    classify_filler,
    classify_matrix,
    classify_method,
    direction_hint,
    filler_props,
    lfa_cp_rho_reported,
    matrix_prefilled,
    matrix_props,
    normalize_direction,
)


@dataclass(frozen=True)
class Derived:
    name: str
    kind: str
    description: str
    unit: str = ""


DERIVED: tuple[Derived, ...] = (
    Derived("paper_id", "string", "Record id (P###) of the source paper."),
    Derived("matrix_family", "string", "epoxy | silicone | polyimide | PEG | polystyrene | polyurethane | other."),
    Derived("filler_family", "string", "BN | AlN | Al2O3 | MgO | hybrid | none | other."),
    Derived("filler_base", "string", "Single-filler label (h-BN, BN, BNNS, cBN, AlN, ...); blank for hybrids."),
    Derived("is_hybrid", "boolean", "More than one filler material."),
    Derived("contains_bn", "boolean", "Any boron nitride component."),
    Derived("method_class", "string", "Measurement technique class (LFA, TPS, THB, HOT_WIRE, SS_D5470, ...)."),
    Derived("method_basis", "string", "named (technique named) | generic | instrument (inferred from model) | none."),
    Derived("method_family", "string", "transient | steady-state | periodic | optical | unspecified."),
    Derived("method_quantity", "string", "Primary measured quantity (diffusivity, conductivity, thermal resistance, ...)."),
    Derived("direction_reported", "string", "k_direction normalized to in-plane | through-plane | isotropic | unknown."),
    Derived("direction_effective", "string", "Best estimate of the direction sensed, incl. 'mixed' for isotropic-mode transient sensors."),
    Derived("direction_basis", "string", "reported | method-text | method-default | none."),
    Derived("phi_vol_pct", "number", "Filler volume percent: reported, or converted from wt% with reference densities.", "vol%"),
    Derived("phi_basis", "string", "reported | converted-from-wt | unavailable-hybrid | unavailable-prefilled-matrix | unavailable."),
    Derived("wt_pct_effective", "number", "Filler weight percent: reported, or converted from vol%.", "wt%"),
    Derived("wt_basis", "string", "reported | converted-from-vol | unavailable..."),
    Derived("rho_filler_used", "number", "Filler density used for a conversion.", "g/cm3"),
    Derived("rho_matrix_used", "number", "Matrix density used for a conversion.", "g/cm3"),
    Derived("k_matrix_effective", "number", "Neat-matrix k: reported, or the matrix-family reference default.", "W/(m K)"),
    Derived("k_matrix_basis", "string", "reported | reference-default | unavailable."),
    Derived("k_enhancement", "number", "k_composite / k_matrix_effective."),
    Derived("log10_k", "number", "log10 of k_composite_W_mK."),
    Derived("k_rel_uncertainty", "number", "Judgement-based 1-sigma relative uncertainty from the method class (paper value not given)."),
    Derived("flags", "string", "Semicolon list of analysis caveats (see docs/ARCHITECTURE.md, 'Bias flags')."),
)
DERIVED_NAMES = tuple(d.name for d in DERIVED)
ENRICHED_COLUMNS = COLUMN_NAMES + DERIVED_NAMES


def _num(v: Any) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def _r(x: float | None, nd: int = 4) -> float | str:
    return "" if x is None else round(x, nd)


def enrich_row(row: dict[str, Any], paper_id: str) -> dict[str, Any]:
    out = dict(row)
    flags: set[str] = set()

    mfam = classify_matrix(row["matrix_polymer"])
    prefilled = matrix_prefilled(row["matrix_polymer"])
    fil = classify_filler(row["filler_material"])
    meth = classify_method(row["measurement_method"])

    # --- direction
    d_rep = normalize_direction(row["k_direction"])
    if d_rep != "unknown":
        d_eff, d_basis = d_rep, "reported"
    elif (h := direction_hint(row["measurement_method"])) != "unknown":
        d_eff, d_basis = h, "method-text"
    elif meth.info.direction in ("through-plane", "mixed"):
        d_eff, d_basis = meth.info.direction, "method-default"
    else:
        d_eff, d_basis = "unknown", "none"

    anisotropic_filler = (fil.base in PLATELET_BN) or (
        fil.is_hybrid and any(c in PLATELET_BN or "BNNS" in c for c in fil.components))
    if meth.info.direction == "mixed" and anisotropic_filler and d_rep != "isotropic":
        flags.add("mixed_direction_anisotropic")
    if meth.method_class in ("SS_D5470", "SS_GHFM", "SS_UNSPECIFIED"):
        flags.add("contact_resistance_included")
    if meth.method_class == "LFA" and not lfa_cp_rho_reported(row["measurement_method"]):
        flags.add("lfa_cp_rho_unreported")
    if meth.method_class == "UNSPECIFIED":
        flags.add("method_unspecified")
    if is_abstract_only(row["source_location"]):
        flags.add("abstract_only")
    if row["value_source"] == "figure":
        flags.add("figure_digitized")
    if prefilled:
        flags.add("matrix_prefilled")
    t = _num(row["measurement_temperature_C"])
    if t is not None and abs(t - 25.0) > 10.0:
        flags.add("non_ambient_temperature")

    # --- loading
    vol, wt = _num(row["filler_loading_vol_pct"]), _num(row["filler_loading_wt_pct"])
    fp = filler_props(fil.base) if fil.base else None
    mp = matrix_props(mfam)
    convertible = fp is not None and mp is not None and not fil.is_hybrid and not prefilled
    why_not = ("unavailable-hybrid" if fil.is_hybrid else
               "unavailable-prefilled-matrix" if prefilled else "unavailable")
    rho_f = rho_m = None
    if vol is not None:
        phi, phi_basis = vol, "reported"
    elif wt is not None and convertible:
        rho_f, rho_m = fp["density"], mp["density"]
        phi, phi_basis = wt_to_vol(wt, rho_f, rho_m), "converted-from-wt"
        if "+" in (row["filler_loading_original_unit"] or ""):
            flags.add("co_filler_ignored_in_conversion")
    else:
        phi, phi_basis = None, why_not
    if wt is not None:
        wt_eff, wt_basis = wt, "reported"
    elif vol is not None and convertible:
        rho_f, rho_m = fp["density"], mp["density"]
        wt_eff, wt_basis = vol_to_wt(vol, rho_f, rho_m), "converted-from-vol"
    else:
        wt_eff, wt_basis = None, why_not

    # --- matrix k
    km = _num(row["k_matrix_W_mK"])
    if km is not None:
        km_eff, km_basis = km, "reported"
    elif mp is not None:
        km_eff, km_basis = float(mp["k"]), "reference-default"
    else:
        km_eff, km_basis = None, "unavailable"

    k = float(row["k_composite_W_mK"])
    rel_u = meth.info.rel_uncertainty
    if meth.method_class == "LFA" and "lfa_cp_rho_unreported" not in flags:
        rel_u = 0.05

    out.update(
        paper_id=paper_id,
        matrix_family=mfam,
        filler_family=fil.family,
        filler_base=fil.base,
        is_hybrid=fil.is_hybrid,
        contains_bn=fil.contains_bn,
        method_class=meth.method_class,
        method_basis=meth.basis,
        method_family=meth.info.family,
        method_quantity=meth.info.quantity,
        direction_reported=d_rep,
        direction_effective=d_eff,
        direction_basis=d_basis,
        phi_vol_pct=_r(phi, 3),
        phi_basis=phi_basis,
        wt_pct_effective=_r(wt_eff, 3),
        wt_basis=wt_basis,
        rho_filler_used=_r(rho_f),
        rho_matrix_used=_r(rho_m),
        k_matrix_effective=_r(km_eff),
        k_matrix_basis=km_basis,
        k_enhancement=_r(k / km_eff if km_eff else None, 3),
        log10_k=_r(math.log10(k), 5),
        k_rel_uncertainty=rel_u,
        flags=";".join(sorted(flags)),
    )
    return out


def enrich_records(records: list[PaperRecord]) -> list[dict[str, Any]]:
    return [enrich_row(measurement_to_row(rec.paper, m), rec.paper_id)
            for rec in records for m in rec.measurements]


def density_check(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Rows reporting BOTH wt% and vol% test the reference densities: convert
    wt% -> vol% and compare with the paper's own vol%."""
    pairs = []
    for r in rows:
        vol, wt = _num(r["filler_loading_vol_pct"]), _num(r["filler_loading_wt_pct"])
        fil = classify_filler(r["filler_material"])
        fp = filler_props(fil.base) if fil.base else None
        mp = matrix_props(r["matrix_family"])
        if vol is None or wt is None or fp is None or mp is None or fil.is_hybrid or wt == 0:
            continue
        conv = wt_to_vol(wt, fp["density"], mp["density"])
        pairs.append({"row_id": r["row_id"], "filler": fil.base, "wt_pct": wt, "vol_reported": vol,
                      "vol_converted": round(conv, 2), "abs_diff": round(conv - vol, 2)})
    diffs = [abs(p["abs_diff"]) for p in pairs]
    return {
        "n_rows": len(pairs),
        "median_abs_diff_vol_pct": round(statistics.median(diffs), 2) if diffs else None,
        "max_abs_diff_vol_pct": round(max(diffs), 2) if diffs else None,
        "within_2_vol_pct": sum(d <= 2 for d in diffs),
        "outliers_gt_5_vol_pct": [p for p in pairs if abs(p["abs_diff"]) > 5],
    }


def qa_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    flag_counts: Counter[str] = Counter()
    for r in rows:
        flag_counts.update(f for f in r["flags"].split(";") if f)
    count = lambda col: dict(Counter(r[col] for r in rows).most_common())  # noqa: E731
    return {
        "rows": len(rows),
        "method_class": count("method_class"),
        "method_basis": count("method_basis"),
        "direction_reported": count("direction_reported"),
        "direction_effective": count("direction_effective"),
        "direction_basis": count("direction_basis"),
        "phi_basis": count("phi_basis"),
        "k_matrix_basis": count("k_matrix_basis"),
        "matrix_family": count("matrix_family"),
        "filler_family": count("filler_family"),
        "flags": dict(flag_counts.most_common()),
        "density_check": density_check(rows),
    }


def _bool_cells(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{k: (str(v).lower() if isinstance(v, bool) else v) for k, v in r.items()} for r in rows]


def expected_enriched_bytes(records: list[PaperRecord]) -> bytes:
    return csv_bytes(_bool_cells(enrich_records(records)), ENRICHED_COLUMNS)
