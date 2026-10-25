"""Independent-extraction check: the same papers, extracted by someone else.

For every DOI present in both ARGUS and an external dataset, each external
point is paired with the closest ARGUS point of the same filler at (nearly) the
same loading and a compatible direction. Agreement says how reproducible the
extraction is; the leftovers point to values one side missed.
"""
from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from .harmonize import _num

# Tolerances for calling two points "the same sample"
PHI_ABS_TOL = 1.0     # vol% or wt% (same basis on both sides)
PHI_REL_TOL = 0.05    # or 5 % of the loading, whichever is larger
AGREE = 0.05          # |dk|/k <= 5 %: agreement (digitizing noise)
MINOR = 0.15          # 5-15 %: minor; above: disagreement to review against the source


def _same_filler(a: dict[str, Any], b: dict[str, Any]) -> bool:
    fa, fb = a["filler_material"], b["filler_material"]
    if fa == fb:
        return True
    bn = {"h-BN", "BN", "BNNS"}
    return fa in bn and fb in bn  # BN written at different levels of detail


def _direction_ok(a: dict[str, Any], b: dict[str, Any]) -> bool:
    da, db = a["direction_reported"], b["direction_reported"]
    return da == db or "unknown" in (da, db) or "isotropic" in (da, db)


def _loading(e: dict[str, Any], a: dict[str, Any]) -> tuple[str, float | None, float | None]:
    """Compare on wt% when both sides REPORT wt% and not both report vol%; else on
    vol% (reported or converted). Converting one side's wt% with reference
    densities would add a density error to the comparison."""
    ev, av = _num(e.get("filler_loading_vol_pct")), _num(a.get("filler_loading_vol_pct"))
    ew, aw = _num(e.get("filler_loading_wt_pct")), _num(a.get("filler_loading_wt_pct"))
    if ew is not None and aw is not None and not (ev is not None and av is not None):
        return "wt", ew, aw
    return "vol", _num(e.get("phi_vol_pct")), _num(a.get("phi_vol_pct"))


def _close(pa: float, pb: float) -> bool:
    return abs(pa - pb) <= max(PHI_ABS_TOL, PHI_REL_TOL * max(pa, pb))


def _grade(rel: float) -> str:
    a = abs(rel)
    return "agree" if a <= AGREE else "minor" if a <= MINOR else "disagree"


def crosscheck(external: list[dict[str, Any]], argus: list[dict[str, Any]]) -> dict[str, Any]:
    by_doi: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for r in argus:
        if r.get("doi"):
            by_doi[r["doi"]].append(r)
    shared = sorted({r["doi"] for r in external if r.get("doi") in by_doi})
    pairs, unmatched_ext, used = [], [], set()
    for doi in shared:
        ours = by_doi[doi]
        for e in (x for x in external if x.get("doi") == doi):
            pe = _num(e.get("phi_vol_pct"))
            cands = []
            for a in ours:
                basis, le, la = _loading(e, a)
                if le is None or la is None or not _same_filler(e, a) or not _direction_ok(e, a) or not _close(le, la):
                    continue
                ke, ka = float(e["k_composite_W_mK"]), float(a["k_composite_W_mK"])
                cands.append((abs(le - la), abs(math.log(ke / ka)), a, basis, le, la))
            if not cands:
                unmatched_ext.append({"doi": doi, "ext_row": e["row_id"], "filler": e["filler_material"],
                                      "phi_vol_pct": pe, "wt_pct": _num(e.get("filler_loading_wt_pct")),
                                      "k": float(e["k_composite_W_mK"]), "direction": e["direction_reported"]})
                continue
            _, _, a, basis, le, la = min(cands, key=lambda c: (c[0], c[1]))
            used.add(a["row_id"])
            ke, ka = float(e["k_composite_W_mK"]), float(a["k_composite_W_mK"])
            rel = (ke - ka) / ka
            pairs.append({"doi": doi, "argus_row": a["row_id"], "ext_row": e["row_id"],
                          "filler": a["filler_material"], "loading_basis": basis,
                          "loading_argus": la, "loading_ext": le, "phi_argus": _num(a.get("phi_vol_pct")),
                          "phi_ext": pe, "phi_basis_argus": a["phi_basis"], "phi_basis_ext": e["phi_basis"],
                          "direction_argus": a["direction_reported"], "direction_ext": e["direction_reported"],
                          "k_argus": ka, "k_ext": ke, "rel_diff": round(rel, 4), "grade": _grade(rel),
                          "argus_value_source": a.get("value_source", ""), "argus_confidence": a.get("confidence", "")})
    # An ARGUS value of unknown direction can be paired with external values in two
    # directions at the same loading; only one of them can be the same measurement.
    # Keep the closer one and report the other as unmatched.
    by_row: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for p in pairs:
        if p["direction_argus"] == "unknown" and p["direction_ext"] not in ("unknown", "isotropic"):
            by_row[p["argus_row"]].append(p)
    drop = set()
    for group in by_row.values():
        if len({p["direction_ext"] for p in group}) > 1:
            keep = min(group, key=lambda p: abs(math.log(p["k_ext"] / p["k_argus"])))
            drop |= {id(p) for p in group if p is not keep}
    for p in [p for p in pairs if id(p) in drop]:
        unmatched_ext.append({"doi": p["doi"], "ext_row": p["ext_row"], "filler": p["filler"], "phi_vol_pct": p["phi_ext"],
                              "wt_pct": None, "k": p["k_ext"], "direction": p["direction_ext"],
                              "note": f"other direction at the loading of ARGUS {p['argus_row']} (direction unknown there)"})
    pairs = [p for p in pairs if id(p) not in drop]
    unmatched_argus = [{"doi": a["doi"], "argus_row": a["row_id"], "filler": a["filler_material"],
                        "phi_vol_pct": _num(a.get("phi_vol_pct")), "wt_pct": _num(a.get("filler_loading_wt_pct")),
                        "k": float(a["k_composite_W_mK"])}
                       for doi in shared for a in by_doi[doi] if a["row_id"] not in used]
    rels = sorted(abs(p["rel_diff"]) for p in pairs)
    grades = defaultdict(int)
    for p in pairs:
        grades[p["grade"]] += 1
    return {
        "shared_papers": len(shared),
        "shared_dois": shared,
        "pairs": len(pairs),
        "grades": dict(grades),
        "median_abs_rel_diff": round(rels[len(rels) // 2], 4) if rels else None,
        "p90_abs_rel_diff": round(rels[min(len(rels) - 1, int(0.9 * len(rels)))], 4) if rels else None,
        "tolerances": {"loading_abs_pct": PHI_ABS_TOL, "loading_rel": PHI_REL_TOL, "agree": AGREE, "minor": MINOR},
        "pair_rows": pairs,
        "unmatched_external": unmatched_ext,
        "unmatched_argus": unmatched_argus,
    }
