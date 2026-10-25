"""Feature matrix for predicting composite k from composition, processing and method.

Target: y = log10(k / k_matrix_effective), the enhancement over the neat matrix
(research report, ML section: log targets, matrix-normalised).

Every feature is a fixed, row-wise function of the enriched row (no statistics
of the dataset are used), so building features cannot leak information across
train/test splits. Anything learned from data (scaling, calibration,
hyper-parameters) happens inside the models, per fold.

Each column belongs to a named group so ablations can ask which kinds of
information help predict an unseen paper.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ..analysis.bias import METHOD_GROUP
from ..physics.emt import maxwell_limit_ratio, nan1997
from ..physics.fit import ASPECT_P  # assumed t/D per filler, shared with the physics fits
from ..vocab import filler_props

FILLER_GROUP = {"h-BN": "hBN", "BN": "hBN", "BNNS": "BNNS", "cBN": "other", "AlN": "AlN",
                "Al2O3": "oxide", "MgO": "oxide",
                # only in the external test sets
                "SiO2": "oxide", "glass": "oxide", "ZnO": "oxide", "Si3N4": "other", "SiC": "other"}
DEFAULT_LOG_SIZE = 1.0  # log10(10 um), a fixed constant (not a data statistic) for missing sizes
YEAR_CENTER = 2020

# column name -> feature group
COLUMNS: dict[str, str] = {
    "phi": "loading", "phi2": "loading",
    "phys_nan": "physics", "phys_maxwell_ceiling": "physics",
    "f_BNNS": "filler", "f_AlN": "filler", "f_oxide": "filler",
    "s_nanosheet": "morphology", "s_particle": "morphology", "s_network": "morphology", "s_other": "morphology",
    "log_size": "morphology", "size_missing": "morphology", "aligned": "morphology",
    "treated": "treatment",
    "d_in_plane": "direction", "d_through_plane": "direction",
    "m_MIXED": "method", "m_STEADY": "method", "m_OTHER": "method", "m_UNSPECIFIED": "method",
    "matrix_epoxy": "matrix", "log_km": "matrix", "km_reported": "matrix",
    "abstract_only": "quality", "figure_digitized": "quality",
    "year_c": "year",
}
NAMES = list(COLUMNS)


def _f(v: Any) -> float | None:
    if isinstance(v, bool) or v in (None, ""):
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _true(v: Any) -> bool:
    return v is True or str(v).lower() == "true"


def shape_group(shape: str, alignment: str) -> str:
    s = f"{shape} {alignment}".lower()
    if any(w in s for w in ("network", "skeleton", "honeycomb", "aerogel", "3d", "scaffold")):
        return "network"
    if "nanosheet" in s or "bnns" in s:
        return "nanosheet"
    if "platelet" in s or "flake" in s:
        return "platelet"
    if any(w in s for w in ("sphere", "particle", "spherical", "irregular")):
        return "particle"
    return "other"


def is_treated(functionalization: str) -> bool:
    t = (functionalization or "").strip().lower()
    return bool(t) and not t.startswith(("none", "no ", "n/a", "not stated", "untreated", "pristine"))


def is_aligned(alignment: str) -> bool:
    a = (alignment or "").strip().lower()
    return bool(a) and "random" not in a


def eligible(r: dict[str, Any]) -> bool:
    """Single-filler rows with a known loading and matrix k (hybrids lack a volume fraction)."""
    phi, km = _f(r["phi_vol_pct"]), _f(r["k_matrix_effective"])
    return (not _true(r["is_hybrid"]) and r["filler_base"] in FILLER_GROUP and phi is not None and phi > 0
            and km is not None and km > 0 and filler_props(r["filler_base"]) is not None)


def physics_log_enhancement(base: str, phi: float, km: float) -> float:
    """log10(k_Nan / km): random orientation, perfect interfaces, intrinsic filler k."""
    props = filler_props(base)
    k = nan1997(phi, km, float(props["k_in_plane"]), float(props["k_through_plane"]), p=ASPECT_P.get(base, 1.0))
    return math.log10(float(k) / km)


@dataclass
class Dataset:
    X: np.ndarray
    y: np.ndarray
    groups: np.ndarray  # paper_id per row
    names: list[str]
    rows: list[dict[str, Any]] = field(default_factory=list)

    @property
    def n_papers(self) -> int:
        return len(set(self.groups.tolist()))

    def columns(self, group_names: set[str] | None = None, drop: set[str] | None = None) -> list[int]:
        keep = []
        for i, n in enumerate(self.names):
            g = COLUMNS[n]
            if (group_names is None or g in group_names) and not (drop and g in drop):
                keep.append(i)
        return keep


def feature_row(r: dict[str, Any]) -> list[float]:
    phi = _f(r["phi_vol_pct"]) / 100.0
    km = _f(r["k_matrix_effective"])
    base = r["filler_base"]
    fg = FILLER_GROUP[base]
    sg = shape_group(r["filler_shape"], r["filler_alignment"])
    size = _f(r["filler_mean_size_um"])
    mg = METHOD_GROUP[r["method_class"]]
    flags = set(str(r["flags"]).split(";"))
    year = _f(r["year"])
    vals = {
        "phi": phi, "phi2": phi * phi,
        "phys_nan": physics_log_enhancement(base, phi, km),
        "phys_maxwell_ceiling": math.log10(float(maxwell_limit_ratio(min(phi, 0.99)))),
        "f_BNNS": fg == "BNNS", "f_AlN": fg == "AlN", "f_oxide": fg in ("oxide", "other"),
        "s_nanosheet": sg == "nanosheet", "s_particle": sg == "particle", "s_network": sg == "network",
        "s_other": sg == "other",
        "log_size": math.log10(size) if size and size > 0 else DEFAULT_LOG_SIZE, "size_missing": not (size and size > 0),
        "aligned": is_aligned(r["filler_alignment"]),
        "treated": is_treated(r["functionalization"]),
        "d_in_plane": r["direction_reported"] == "in-plane", "d_through_plane": r["direction_reported"] == "through-plane",
        "m_MIXED": mg == "MIXED", "m_STEADY": mg == "STEADY", "m_OTHER": mg == "OTHER", "m_UNSPECIFIED": mg == "UNSPECIFIED",
        "matrix_epoxy": r["matrix_family"] == "epoxy", "log_km": math.log10(km),
        "km_reported": r["k_matrix_basis"] == "reported",
        "abstract_only": "abstract_only" in flags, "figure_digitized": "figure_digitized" in flags,
        "year_c": (year - YEAR_CENTER) if year is not None else 0.0,
    }
    return [float(vals[n]) for n in NAMES]


def build_dataset(rows: list[dict[str, Any]]) -> Dataset:
    sel = [r for r in rows if eligible(r)]
    X = np.array([feature_row(r) for r in sel], dtype=float)
    y = np.array([math.log10(float(r["k_composite_W_mK"]) / _f(r["k_matrix_effective"])) for r in sel])
    groups = np.array([r["paper_id"] for r in sel])
    return Dataset(X=X, y=y, groups=groups, names=list(NAMES), rows=sel)
