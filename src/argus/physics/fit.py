"""Fit effective-medium models to loading series in the dataset.

A *series* is a set of rows from one paper that differ only in filler loading
(same matrix, filler, size, treatment, processing, method and direction). Each
model gets ONE free parameter, fitted by least squares on log10(k):

  maxwell_kf   Maxwell-Garnett with an apparent filler conductivity kf_app
  ln_A         Lewis-Nielsen shape factor A (kf = reference, phi_m fixed by shape)
  agari        Agari-Uno: two parameters, but linear in log k (closed form)
  nan_rk       Nan 1997, random orientation, apparent interfacial resistance R_K
               with ASSUMED geometry (lateral size from the row, else 10 um;
               p = 0.05 for h-BN/BN platelets, 0.01 for BNNS, 1 for particles)

Fitted parameters are "apparent": they absorb voids, dispersion, contact and
measurement-direction effects (research report, physics section). They are a
diagnostic for comparing papers, not interface physics.
"""
from __future__ import annotations

import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np
from scipy.optimize import minimize_scalar

from ..vocab import classify_filler, filler_props
from .emt import lewis_nielsen, maxwell_garnett, maxwell_limit_ratio, nan1997

SERIES_KEY = ("doi", "matrix_polymer", "curing_agent", "filler_material", "filler_shape", "filler_mean_size_um",
              "functionalization", "filler_alignment", "processing_method", "k_direction", "measurement_method",
              "measurement_temperature_C")

DEFAULT_SIZE_UM = 10.0
ASPECT_P = {"h-BN": 0.05, "BN": 0.05, "BNNS": 0.01}  # p = t/D (assumed)
PHI_M = {"platelet": 0.52, "sphere": 0.637}  # Nielsen: 3D-random rods (proxy for plates), random close spheres


@dataclass
class SeriesFit:
    key: tuple
    paper_id: str
    doi: str
    filler: str
    shape_class: str
    direction: str
    method_class: str
    phi: list[float]
    k: list[float]
    km: float
    km_basis: str
    kf_ref: float
    fits: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def best(self) -> str:
        ok = {m: f["rmse_log10"] for m, f in self.fits.items() if f.get("rmse_log10") is not None}
        return min(ok, key=ok.get) if ok else ""


def _f(v: Any) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and v != "" else None


def shape_class(base: str) -> str:
    return "platelet" if base in ASPECT_P else "sphere"


def isotropic_kf(props: dict[str, Any]) -> float:
    """Orientation-averaged intrinsic k for models that take a scalar kf."""
    a, b = float(props["k_in_plane"]), float(props["k_through_plane"])
    return (2 * a + b) / 3


def build_series(rows: list[dict[str, Any]], min_points: int = 3) -> list[SeriesFit]:
    groups: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        fil = classify_filler(r["filler_material"])
        phi = _f(r["phi_vol_pct"])
        if fil.is_hybrid or not fil.base or filler_props(fil.base) is None or phi is None or phi <= 0:
            continue
        groups[tuple(r[c] for c in SERIES_KEY)].append(r)
    out = []
    for key, g in groups.items():
        pts = sorted({(_f(r["phi_vol_pct"]) / 100.0, float(r["k_composite_W_mK"])) for r in g})
        if len({p for p, _ in pts}) < min_points:
            continue
        reported = [_f(r["k_matrix_W_mK"]) for r in g if r["k_matrix_basis"] == "reported"]
        km = reported[0] if reported else float(g[0]["k_matrix_effective"])
        base = classify_filler(g[0]["filler_material"]).base
        out.append(SeriesFit(
            key=key, paper_id=g[0]["paper_id"], doi=g[0]["doi"], filler=base, shape_class=shape_class(base),
            direction=g[0]["direction_effective"], method_class=g[0]["method_class"],
            phi=[p for p, _ in pts], k=[k for _, k in pts], km=km,
            km_basis="reported" if reported else "reference-default",
            kf_ref=isotropic_kf(filler_props(base)),
        ))
    return sorted(out, key=lambda s: (s.paper_id, s.key))


def _fit_1d(model: Callable[[float], np.ndarray], k: np.ndarray, lo: float, hi: float) -> tuple[float, float]:
    """Minimize the RMS log10 residual over log10(param) in [lo, hi]."""
    y = np.log10(k)

    def loss(lp: float) -> float:
        pred = model(10 ** lp)
        if not np.all(np.isfinite(pred)) or np.any(pred <= 0):
            return 1e6
        return float(np.mean((np.log10(pred) - y) ** 2))

    res = minimize_scalar(loss, bounds=(math.log10(lo), math.log10(hi)), method="bounded",
                          options={"xatol": 1e-6})
    return 10 ** res.x, math.sqrt(res.fun)


def fit_series(s: SeriesFit) -> SeriesFit:
    phi, k, km = np.array(s.phi), np.array(s.k), s.km
    edge = lambda v, lo, hi: bool(v <= lo * 1.01 or v >= hi * 0.99)  # noqa: E731

    # Maxwell with apparent kf
    lo, hi = km * 1.001, 1e5
    kf_app, rmse = _fit_1d(lambda kf: maxwell_garnett(phi, km, kf), k, lo, hi)
    s.fits["maxwell_kf"] = {"kf_apparent": kf_app, "rmse_log10": rmse, "at_bound": edge(kf_app, lo, hi)}

    # Lewis-Nielsen, fit A with kf = reference and phi_m by shape
    phi_m = PHI_M[s.shape_class]
    if phi.max() < phi_m:
        lo, hi = 0.01, 1e4
        A, rmse = _fit_1d(lambda a: lewis_nielsen(phi, km, s.kf_ref, a, phi_m), k, lo, hi)
        s.fits["ln_A"] = {"A": A, "phi_m": phi_m, "rmse_log10": rmse if rmse < 999 else None, "at_bound": edge(A, lo, hi)}
    else:
        s.fits["ln_A"] = {"A": None, "phi_m": phi_m, "rmse_log10": None, "at_bound": False,
                          "note": f"max loading {phi.max():.2f} >= phi_m"}

    # Agari-Uno: log10 k = a + b phi, closed form (2 parameters)
    b, a = np.polyfit(phi, np.log10(k), 1)
    resid = (a + b * phi) - np.log10(k)
    C1 = 10 ** a / km
    C2 = (b + a) / math.log10(s.kf_ref)
    s.fits["agari"] = {"C1": C1, "C2": C2, "rmse_log10": float(np.sqrt(np.mean(resid ** 2)))}

    # Nan 1997, random orientation, apparent R_K with assumed geometry
    props = filler_props(s.filler)
    size_um = _f(s.key[SERIES_KEY.index("filler_mean_size_um")]) or DEFAULT_SIZE_UM
    a1 = size_um * 1e-6 / 2
    p = ASPECT_P.get(s.filler, 1.0)
    kpar, kperp = float(props["k_in_plane"]), float(props["k_through_plane"])
    model = lambda rk: nan1997(phi, km, kpar, kperp, p=p, r_k=rk, a1_m=a1)  # noqa: E731
    lo, hi = 1e-11, 1e-4
    rk, rmse = _fit_1d(model, k, lo, hi)
    under = bool(np.mean(np.log10(nan1997(phi, km, kpar, kperp, p=p)) - np.log10(k)) < 0)
    s.fits["nan_rk"] = {"R_K_m2K_W": rk, "convention": "semi-axis (Nan 1997)", "p_assumed": p,
                        "size_um": size_um, "size_assumed": size_um == DEFAULT_SIZE_UM and not
                        _f(s.key[SERIES_KEY.index("filler_mean_size_um")]),
                        "rmse_log10": rmse, "at_bound": edge(rk, lo, hi),
                        "data_above_perfect_interface_prediction": under}
    return s


def maxwell_ceiling_share(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Share of rows whose k/km exceeds the Maxwell kf -> infinity ceiling
    (1 + 2 phi)/(1 - phi): no isolated-sphere model can reach them."""
    n = above = 0
    for r in rows:
        phi, km = _f(r["phi_vol_pct"]), _f(r["k_matrix_effective"])
        if phi is None or km is None or not 0 < phi < 100:
            continue
        n += 1
        above += float(r["k_composite_W_mK"]) / km > float(maxwell_limit_ratio(phi / 100))
    return {"rows_with_phi": n, "above_maxwell_ceiling": above,
            "share": round(above / n, 3) if n else None}


N_PARAMS = {"maxwell_kf": 1, "ln_A": 1, "agari": 2, "nan_rk": 1}


def _sig(x: float, n: int = 4) -> float:
    return float(f"{x:.{n}g}")


def summarize(fits: list[SeriesFit], rows: list[dict[str, Any]]) -> dict[str, Any]:
    models = list(N_PARAMS)
    med = lambda xs: _sig(statistics.median(xs)) if xs else None  # noqa: E731

    def q(xs: list[float]) -> list[float] | None:
        if len(xs) < 4:
            return None
        qs = statistics.quantiles(xs, n=4)
        return [_sig(qs[0], 3), _sig(qs[2], 3)]

    out: dict[str, Any] = {
        "series": len(fits),
        "points": sum(len(s.phi) for s in fits),
        "papers": len({s.doi for s in fits}),
        "by_filler": dict(Counter(s.filler for s in fits).most_common()),
        "free_parameters": N_PARAMS,
        "best_model_count": dict(Counter(s.best for s in fits).most_common()),
        "note": "best_model compares RMSE only; agari has 2 free parameters vs 1 for the others, "
                "so with 3-5 points per series it is favoured by construction.",
        "median_rmse_log10": {m: med([s.fits[m]["rmse_log10"] for s in fits
                                     if s.fits[m].get("rmse_log10") is not None]) for m in models},
        "maxwell_ceiling": maxwell_ceiling_share(rows),
    }
    kf = [s.fits["maxwell_kf"]["kf_apparent"] for s in fits if not s.fits["maxwell_kf"]["at_bound"]]
    A = [s.fits["ln_A"]["A"] for s in fits if s.fits["ln_A"].get("A") and not s.fits["ln_A"]["at_bound"]]
    rk = [s.fits["nan_rk"]["R_K_m2K_W"] for s in fits if not s.fits["nan_rk"]["at_bound"]]
    c2 = [s.fits["agari"]["C2"] for s in fits]
    out["parameters"] = {
        "maxwell_kf_apparent": {"n": len(kf), "median": med(kf), "iqr": q(kf),
                                "series_at_upper_bound": sum(s.fits["maxwell_kf"]["at_bound"] for s in fits)},
        "lewis_nielsen_A": {"n": len(A), "median": med(A), "iqr": q(A)},
        "agari_C2": {"n": len(c2), "median": med(c2), "iqr": q(c2)},
        "nan_R_K_m2K_W": {"n": len(rk), "median": _sig(statistics.median(rk), 3) if rk else None,
                          "iqr": q(rk), "convention": "semi-axis (Nan 1997)",
                          "series_above_perfect_interface": sum(
                              s.fits["nan_rk"]["data_above_perfect_interface_prediction"] for s in fits)},
    }
    return out


def fits_table(fits: list[SeriesFit]) -> list[dict[str, Any]]:
    rows = []
    for s in fits:
        f = s.fits
        rows.append({
            "paper_id": s.paper_id, "doi": s.doi, "filler": s.filler, "direction": s.direction,
            "method_class": s.method_class, "n_points": len(s.phi),
            "phi_min": round(min(s.phi), 4), "phi_max": round(max(s.phi), 4),
            "k_min": min(s.k), "k_max": max(s.k), "k_matrix": s.km, "k_matrix_basis": s.km_basis,
            "best_model": s.best,
            "maxwell_kf_apparent": f"{f['maxwell_kf']['kf_apparent']:.4g}",
            "maxwell_rmse_log10": round(f["maxwell_kf"]["rmse_log10"], 4),
            "ln_A": "" if f["ln_A"].get("A") is None else f"{f['ln_A']['A']:.4g}",
            "ln_rmse_log10": "" if f["ln_A"].get("rmse_log10") is None else round(f["ln_A"]["rmse_log10"], 4),
            "agari_C1": f"{f['agari']['C1']:.4g}", "agari_C2": f"{f['agari']['C2']:.4g}",
            "agari_rmse_log10": round(f["agari"]["rmse_log10"], 4),
            "nan_R_K_m2K_W": f"{f['nan_rk']['R_K_m2K_W']:.3g}",
            "nan_rmse_log10": round(f["nan_rk"]["rmse_log10"], 4),
            "nan_size_um": f["nan_rk"]["size_um"], "nan_p_assumed": f["nan_rk"]["p_assumed"],
            "nan_data_above_perfect_interface": f["nan_rk"]["data_above_perfect_interface_prediction"],
        })
    return rows
