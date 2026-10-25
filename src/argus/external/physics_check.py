"""Cross-check of argus.physics.emt against two independent implementations.

Both external workbooks publish, next to every measured point, the model
predictions their authors computed. Feeding the same inputs to our functions
and comparing is a test of our code that does not depend on our own reading of
the equations:

  EVF (Anastasiou 2026): Hill (Voigt-Reuss mean), Maxwell, symmetric
      Bruggeman and Nan's spherical form with an interfacial resistance, which is
      the Hasselman-Johnson equation.
  BCC (He, Wu & Fu 2025): Maxwell-Garnett, Hasselman-Johnson with the fitted
      interfacial resistance, and asymmetric Bruggeman (differential effective
      medium, no interface resistance).

For the asymmetric Bruggeman model the comparison also reports how well each
side satisfies the model's defining equation, (1 - phi) = (kf - k)/(kf - km) *
(km / k)^(1/3): a difference can only be blamed on our code if our root fails
that equation.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Callable

import numpy as np

from ..physics import emt
from .sources import bcc, evf

EXACT = 1e-9      # relative difference treated as identical (floating point)
CLOSE = 1e-4


def _summary(diffs: list[float]) -> dict[str, Any]:
    a = np.array(diffs, dtype=float)
    if not len(a):
        return {"n": 0}
    return {"n": int(len(a)), "max_rel_diff": float(f"{a.max():.3g}"), "median_rel_diff": float(f"{np.median(a):.3g}"),
            "n_exact": int((a <= EXACT).sum()), "n_close": int((a <= CLOSE).sum())}


def _rel(ours: float, theirs: float) -> float:
    return abs(ours / theirs - 1.0)


def dem_residual(k: float, phi: float, km: float, kf: float) -> float:
    """Residual of the asymmetric Bruggeman equation at k (0 for an exact root)."""
    return (kf - k) / (kf - km) * (km / k) ** (1.0 / 3.0) - (1.0 - phi)


def check_evf(folder: Path) -> dict[str, Any]:
    rows = evf.model_columns(folder)
    ours: dict[str, Callable[[dict[str, Any]], float | None]] = {
        "maxwell": lambda r: float(emt.maxwell_garnett(r["phi"], r["km"], r["kf"])),
        "bruggeman": lambda r: float(emt.bruggeman_symmetric(r["phi"], r["km"], r["kf"])),
        "hill": lambda r: 0.5 * (float(emt.parallel(r["phi"], r["km"], r["kf"])) + float(emt.series(r["phi"], r["km"], r["kf"]))),
        "nan": lambda r: (float(emt.hasselman_johnson(r["phi"], r["km"], r["kf"], r["radius_m"], r["r_bd"]))
                          if r["radius_m"] and r["r_bd"] is not None else None),
    }
    out = {}
    for name, fn in ours.items():
        diffs = []
        for r in rows:
            v, t = fn(r), r.get(name)
            if v is not None and t:
                diffs.append(_rel(v, t))
        out[name] = _summary(diffs)
    out["models_compared"] = {"maxwell": "maxwell_garnett", "bruggeman": "bruggeman_symmetric",
                              "hill": "(parallel + series) / 2", "nan": "hasselman_johnson (Nan 1997, spheres)"}
    return out


def check_bcc(folder: Path) -> dict[str, Any]:
    pts = bcc.points(folder)
    mg, hj, dem = [], [], []
    dem_bad = []
    for p in pts:
        km, kf, phi = p["km"], p["kf"], p["phi"]
        m = p["model"]
        if m["maxwell_garnett"]:
            mg.append(_rel(float(emt.maxwell_garnett(phi, km, kf)), m["maxwell_garnett"]))
        if m["hasselman_johnson"]:
            hj.append(_rel(float(emt.hasselman_johnson(phi, km, kf, p["radius_m"], p["r_i"])), m["hasselman_johnson"]))
        if m["bruggeman"]:
            k_ours = float(emt.bruggeman_dem(phi, km, kf))
            d = _rel(k_ours, m["bruggeman"])
            dem.append(d)
            if d > CLOSE:
                dem_bad.append({"sheet_row": p["sheet_row"], "km": km, "kf": kf, "vf_pct": round(p["vf_pct"], 3),
                                "k_theirs": round(m["bruggeman"], 6), "k_ours": round(k_ours, 6),
                                "residual_theirs": float(f"{dem_residual(m['bruggeman'], phi, km, kf):.3g}"),
                                "residual_ours": float(f"{dem_residual(k_ours, phi, km, kf):.3g}")})
    res_ours = [abs(b["residual_ours"]) for b in dem_bad]
    res_theirs = [abs(b["residual_theirs"]) for b in dem_bad]
    return {
        "maxwell_garnett": _summary(mg),
        "hasselman_johnson": _summary(hj),
        "bruggeman_dem": {**_summary(dem),
                          "disagreements": len(dem_bad),
                          "max_abs_residual_ours": max(res_ours) if res_ours else None,
                          "min_abs_residual_theirs": min(res_theirs) if res_theirs else None,
                          "rows": dem_bad},
        "models_compared": {"maxwell_garnett": "maxwell_garnett", "hasselman_johnson": "hasselman_johnson (radius = 2r/2)",
                            "bruggeman_dem": "bruggeman_dem (r_k = 0)"},
    }


def accuracy_on_bcc(folder: Path, polymer_km_max: float = 1.0) -> dict[str, Any]:
    """How well each model predicts the measured k of the polymer-matrix BCC points
    (km < 1 W/(m K)), by loading band. Uses interface-free forms only: the sheet's
    Ri was fitted to these same points, so models using it are not predictions."""
    pts = [p for p in bcc.points(folder) if p["km"] < polymer_km_max]
    bands = [(0.0, 0.2), (0.2, 0.4), (0.4, 1.0)]
    models: dict[str, Callable[[dict[str, Any]], float]] = {
        "maxwell_garnett": lambda p: float(emt.maxwell_garnett(p["phi"], p["km"], p["kf"])),
        "bruggeman_symmetric": lambda p: float(emt.bruggeman_symmetric(p["phi"], p["km"], p["kf"])),
        "bruggeman_dem": lambda p: float(emt.bruggeman_dem(p["phi"], p["km"], p["kf"])),
        "lewis_nielsen_spheres": lambda p: float(emt.lewis_nielsen(p["phi"], p["km"], p["kf"], A=1.5, phi_m=0.637)),
    }
    phi = np.array([p["phi"] for p in pts])
    band_masks = {f"{int(lo * 100)}-{int(hi * 100)} vol%": (phi >= lo) & (phi < hi) for lo, hi in bands}
    out: dict[str, Any] = {"n_points": len(pts), "km_max": polymer_km_max,
                           "n_by_band": {b: int(m.sum()) for b, m in band_masks.items()}, "models": {}}
    for name, fn in models.items():
        pred = np.array([fn(p) for p in pts])
        ok = np.isfinite(pred) & (pred > 0)
        err = np.full(len(pts), np.nan)
        err[ok] = np.log10(pred[ok] / np.array([p["k_exp"] for p in pts])[ok])
        entry: dict[str, Any] = {"n": int(ok.sum()), "diverged": int((~ok).sum()),
                                 "mae_log10": round(float(np.nanmean(np.abs(err))), 4),
                                 "bias_log10": round(float(np.nanmean(err)), 4), "mae_by_band": {}}
        for b, m in band_masks.items():
            if (m & ok).any():
                entry["mae_by_band"][b] = round(float(np.nanmean(np.abs(err[m & ok]))), 4)
        out["models"][name] = entry
    ceiling = np.array([p["km"] * float(emt.maxwell_limit_ratio(min(p["phi"], 0.999))) for p in pts])
    above = np.array([p["k_exp"] for p in pts]) > ceiling
    out["above_maxwell_ceiling"] = {"n": int(above.sum()), "share": round(float(above.mean()), 3) if pts else None,
                                    "share_by_band": {b: round(float(above[m].mean()), 3) for b, m in band_masks.items() if m.any()}}
    return out
