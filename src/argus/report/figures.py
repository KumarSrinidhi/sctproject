"""Static figures for the course report (matplotlib, light theme).

Palette and mark rules follow the project's dataviz reference: categorical
slots blue / orange / aqua (validated all-pairs for scatter), thin solid
gridlines, >= 8 px markers with a surface ring, emphasis (accent vs gray)
where one group is the point, dumbbells for paired values, and small
multiples instead of a fourth hue.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from ..physics.emt import maxwell_limit_ratio, nan1997
from ..vocab import filler_props

PAL = {
    "surface": "#fcfcfb", "ink": "#0b0b0b", "ink2": "#52514e", "muted": "#898781",
    "grid": "#e1e0d9", "axis": "#c3c2b7",
    "s1": "#2a78d6", "s1_light": "#86b6ef", "s2": "#eb6834", "s3": "#1baf7a",
}
MARKER = 36  # points^2 -> ~8 px at 150 dpi export
RING = 1.2


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 9,
        "axes.titlesize": 10, "axes.titleweight": "semibold", "axes.titlecolor": PAL["ink"],
        "axes.labelcolor": PAL["ink2"], "axes.labelsize": 9,
        "axes.facecolor": PAL["surface"], "figure.facecolor": PAL["surface"], "savefig.facecolor": PAL["surface"],
        "axes.edgecolor": PAL["axis"], "axes.linewidth": 1.0,
        "xtick.color": PAL["muted"], "ytick.color": PAL["muted"],
        "xtick.labelcolor": PAL["ink2"], "ytick.labelcolor": PAL["ink2"],
        "legend.frameon": False, "legend.fontsize": 8.5, "legend.labelcolor": PAL["ink2"],
        "lines.solid_capstyle": "round", "lines.solid_joinstyle": "round",
    })
    return plt


def _clean(ax, grid: str = "y") -> None:
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(True, axis=grid, color=PAL["grid"], linewidth=0.8, linestyle="-")
    ax.set_axisbelow(True)
    ax.tick_params(length=3, width=0.8)


def _sci(x: float) -> str:
    """6.81e-07 -> '6.8×10⁻⁷' (matplotlib-safe unicode superscripts)."""
    e = int(math.floor(math.log10(abs(x))))
    return f"{x / 10 ** e:.1f}×10{str(e).translate(str.maketrans('-0123456789', '⁻⁰¹²³⁴⁵⁶⁷⁸⁹'))}"


def _f(v: Any) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _save(fig, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches="tight", pad_inches=0.08)
    import matplotlib.pyplot as plt

    plt.close(fig)
    return path


# --------------------------------------------------------------------------- 0. overview

def fig_overview(rows: list[dict[str, Any]], path: Path) -> Path:
    plt = _plt()
    fig, (a, b) = plt.subplots(1, 2, figsize=(9.6, 3.4), gridspec_kw={"width_ratios": [1.05, 1]})
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["method_class"]] = counts.get(r["method_class"], 0) + 1
    names = sorted(counts, key=lambda n: counts[n])
    label = {"UNSPECIFIED": "not stated", "SS_D5470": "steady-state (D5470-type)", "LFA": "laser flash (LFA)",
             "THB": "transient hot bridge", "TPS": "Hot Disk / TPS", "HOT_WIRE": "hot wire", "PERIODIC": "periodic heating",
             "SS_GHFM": "guarded heat flow", "IR_THERMO": "IR thermography", "SS_UNSPECIFIED": "steady-state, unspecified"}
    y = np.arange(len(names))
    a.barh(y, [counts[n] for n in names], height=0.62, color=PAL["s1"])
    for yi, n in zip(y, names):
        a.text(counts[n] + 1.5, yi, str(counts[n]), va="center", color=PAL["ink2"], fontsize=8.5)
    a.set_yticks(y, [label.get(n, n) for n in names])
    a.set_xlabel("rows")
    a.set_title("Measurement technique per row", loc="left")
    _clean(a, "x")
    a.tick_params(axis="y", length=0)

    k = np.array([float(r["k_composite_W_mK"]) for r in rows])
    bins = np.logspace(np.log10(0.1), np.log10(60), 26)
    b.hist(k, bins=bins, color=PAL["s1"], edgecolor=PAL["surface"], linewidth=1.5)
    b.set_xscale("log")
    b.set_xlabel("composite k (W/m·K)")
    b.set_ylabel("rows")
    med = float(np.median(k))
    b.axvline(med, color=PAL["ink2"], lw=1)
    b.text(med * 1.08, b.get_ylim()[1] * 0.92, f"median {med:.2f}", color=PAL["ink2"], fontsize=8.5, va="top")
    b.set_title(f"Distribution of k ({len(k)} rows)", loc="left")
    _clean(b, "y")
    fig.tight_layout()
    return _save(fig, path)


# --------------------------------------------------------------------------- 1. k vs loading

PANELS = (
    ("h-BN / BN platelets", {"h-BN", "BN"}, "h-BN", 0.05),
    ("BN nanosheets (BNNS)", {"BNNS"}, "BNNS", 0.01),
    ("AlN and oxide particles", {"AlN", "Al2O3", "MgO"}, "AlN", 1.0),
)


def model_curves(base: str, p: float, rk: float, km: float = 0.2, size_um: float = 10.0) -> dict[str, np.ndarray]:
    phi = np.linspace(0.002, 0.8, 240)
    props = filler_props(base)
    kpar, kperp = float(props["k_in_plane"]), float(props["k_through_plane"])
    ceiling = maxwell_limit_ratio(phi)
    nan0 = nan1997(phi, km, kpar, kperp, p=p) / km
    nanr = nan1997(phi, km, kpar, kperp, p=p, r_k=rk, a1_m=size_um * 1e-6 / 2) / km
    for arr in (nan0, nanr):
        arr[(arr <= 0) | ~np.isfinite(arr)] = np.nan
    return {"phi_pct": phi * 100, "ceiling": ceiling, "nan0": nan0, "nanr": nanr}


def fig_k_vs_loading(rows: list[dict[str, Any]], rk_median: float, path: Path) -> Path:
    plt = _plt()
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.7), sharey=True)
    handles = None
    hp = None
    for ax, (title, bases, ref, p) in zip(axes, PANELS):
        pts = [(float(r["phi_vol_pct"]), float(r["k_composite_W_mK"]) / float(r["k_matrix_effective"]), r["paper_id"])
               for r in rows if r["filler_base"] in bases and _f(r["phi_vol_pct"]) and _f(r["k_matrix_effective"])
               and str(r["is_hybrid"]).lower() != "true"]
        c = model_curves(ref, p, rk_median)
        h_ceiling, = ax.plot(c["phi_pct"], c["ceiling"], color=PAL["ink2"], lw=1.2, ls=(0, (4, 3)),
                             label="Maxwell ceiling (filler k → ∞)")
        h0, = ax.plot(c["phi_pct"], c["nan0"], color=PAL["s2"], lw=2, label="Nan 1997, perfect interfaces")
        hr, = ax.plot(c["phi_pct"], c["nanr"], color=PAL["s3"], lw=2,
                      label=f"Nan 1997, R_K = {_sci(rk_median)} m²K/W (median fit)")
        if pts:
            x, y, _ = zip(*pts)
            hp = ax.scatter(x, y, s=MARKER, color=PAL["s1"], edgecolor=PAL["surface"], linewidth=RING, zorder=3,
                            label="measured k / k_m")
        ax.set_yscale("log")
        ax.set_xlim(0, 82)
        ax.set_ylim(0.8, 400)
        n_p = len({q[2] for q in pts})
        ax.set_title(f"{title}\n{len(pts)} rows, {n_p} papers", loc="left", fontsize=9.5)
        ax.set_xlabel("filler loading (vol%)")
        _clean(ax, "both")
        handles = [h for h in (hp, h0, hr, h_ceiling) if h is not None]
    axes[0].set_ylabel("enhancement k / k_matrix")
    fig.legend(handles=handles, loc="upper center", ncol=4, bbox_to_anchor=(0.5, 1.07))
    fig.tight_layout()
    return _save(fig, path)


# --------------------------------------------------------------------------- 2. method bias

def fig_method_bias(bias: dict[str, Any], path: Path) -> Path:
    plt = _plt()
    pairs = bias["direction_pairs"]
    main = bias["pooled_models"]["main"]
    fig, (a, b) = plt.subplots(1, 2, figsize=(10.2, 3.9), gridspec_kw={"width_ratios": [1, 1.05]})

    labels = []
    for i, pr in enumerate(pairs):
        phi = f", {pr['phi_vol_pct']:.1f} vol%" if pr.get("phi_vol_pct") else ""
        labels.append(f"{pr['paper_id']} {pr['filler']}{phi}")
        a.plot([pr["k_b"], pr["k_a"]], [i, i], color=PAL["axis"], lw=2, zorder=1)
    y = np.arange(len(pairs))
    a.scatter([pr["k_b"] for pr in pairs], y, s=MARKER * 1.3, color=PAL["s1_light"], edgecolor=PAL["surface"],
              linewidth=RING, zorder=3, label="through-plane")
    a.scatter([pr["k_a"] for pr in pairs], y, s=MARKER * 1.3, color=PAL["s1"], edgecolor=PAL["surface"],
              linewidth=RING, zorder=3, label="in-plane")
    for i, pr in enumerate(pairs):
        a.text(max(pr["k_a"], pr["k_b"]) * 1.18, i, f"A = {pr['ratio']:.1f}", va="center", color=PAL["ink2"], fontsize=8.5)
    a.set_xscale("log")
    a.set_xlim(0.15, 40)
    a.set_yticks(y, labels)
    a.invert_yaxis()
    a.set_xlabel("k (W/m·K), same sample")
    a.set_title("Same sample, two directions", loc="left")
    a.legend(loc="upper right")
    _clean(a, "x")
    a.tick_params(axis="y", length=0)

    order = [("method:MIXED", "Hot Disk / THB / hot wire vs LFA"), ("method:STEADY", "steady-state vs LFA"),
             ("method:UNSPECIFIED", "method not stated vs LFA"), ("method:OTHER", "periodic / IR vs LFA"),
             ("in_plane", "reported in-plane"), ("BNNS", "BNNS vs h-BN/BN")]
    eff = [(lab, main["effects"][k]) for k, lab in order if k in main["effects"]]
    yy = np.arange(len(eff))
    for i, (lab, e) in enumerate(eff):
        lo, hi = e["ci95"]
        b.plot([lo, hi], [i, i], color=PAL["s1"], lw=2, zorder=2)
        papers = f"  ({e['papers']} papers)" if e.get("papers") else ""
        b.text(hi * 1.12, i, f"×{e['factor']:.2f}{papers}", va="center", color=PAL["ink2"], fontsize=8.5)
    b.scatter([e["factor"] for _, e in eff], yy, s=MARKER * 1.3, color=PAL["s1"], edgecolor=PAL["surface"],
              linewidth=RING, zorder=3)
    b.axvline(1, color=PAL["ink2"], lw=1)
    b.set_xscale("log")
    b.set_xlim(0.1, 60)
    b.set_yticks(yy, [lab for lab, _ in eff])
    b.invert_yaxis()
    b.set_xlabel("multiplicative effect on k (95% CI), between papers")
    b.set_title(f"Mixed model, {main['n']} rows / {main['papers']} papers", loc="left")
    _clean(b, "x")
    b.tick_params(axis="y", length=0)
    fig.tight_layout()
    return _save(fig, path)


# --------------------------------------------------------------------------- 3. interfacial resistance

def fig_interface_resistance(fits: list[Any], path: Path) -> Path:
    plt = _plt()
    fig, ax = plt.subplots(figsize=(8.4, 2.9))
    ax.axvspan(1e-8, 2.4e-6, color=PAL["s1"], alpha=0.08, lw=0)
    ax.text(1.1e-8, 2.42, "published BN/epoxy model fits", color=PAL["ink2"], fontsize=8.5, va="center")
    ax.axvspan(2.4e-9, 3.6e-9, color=PAL["ink2"], alpha=0.18, lw=0)
    ax.text(3.9e-9, -0.42, "molecular dynamics", color=PAL["ink2"], fontsize=8.5, va="center")
    groups = {"h-BN": 0, "BN": 0, "BNNS": 1}
    rng = np.random.default_rng(0)
    free, bound = [], []
    for s in fits:
        f = s.fits["nan_rk"]
        yv = groups.get(s.filler, 2) + rng.uniform(-0.18, 0.18)
        (bound if f["at_bound"] else free).append((f["R_K_m2K_W"], yv))
    if free:
        x, y = zip(*free)
        ax.scatter(x, y, s=MARKER * 1.4, color=PAL["s1"], edgecolor=PAL["surface"], linewidth=RING, zorder=3,
                   label="fitted series")
        med = float(np.median(x))
        ax.axvline(med, color=PAL["s1"], lw=1)
        ax.text(med * 1.1, -0.42, f"median {_sci(med)}", color=PAL["ink2"], fontsize=8.5, va="center")
    if bound:
        _, y = zip(*bound)
        ax.scatter([1.3e-9] * len(y), y, s=MARKER * 1.4, facecolor=PAL["surface"], edgecolor=PAL["s1"], linewidth=1.5,
                   zorder=3, label="above perfect-interface prediction (R_K → 0)")
    ax.set_xscale("log")
    ax.set_xlim(1e-9, 1e-4)
    ax.set_ylim(-0.7, 2.7)
    ax.set_yticks([0, 1], ["h-BN / BN", "BNNS"])
    ax.set_xlabel("apparent interfacial resistance R_K (m²K/W), Nan 1997 semi-axis convention")
    ax.set_title("Interfacial resistance needed to explain each loading series", loc="left")
    ax.legend(loc="upper right")
    _clean(ax, "x")
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    return _save(fig, path)


# --------------------------------------------------------------------------- 4-6. machine learning

def fig_parity(pred_rows: list[dict[str, Any]], ml: dict[str, Any], path: Path) -> Path:
    plt = _plt()
    best = ml["best_model"]
    models = [m for m in ("physics", "knn", best) if m in ml["models"]]
    fig, axes = plt.subplots(1, len(models), figsize=(3.45 * len(models), 3.5), sharex=True, sharey=True)
    k = np.array([float(r["k_measured"]) for r in pred_rows])
    lo, hi = 0.1, 60
    for ax, m in zip(np.atleast_1d(axes), models):
        kp = np.array([float(r[f"k_pred_{m}"]) for r in pred_rows])
        met = ml["models"][m]["lopo"]
        ax.fill_between([lo, hi], [lo / 2, hi / 2], [lo * 2, hi * 2], color=PAL["grid"], alpha=0.7, lw=0)
        ax.plot([lo, hi], [lo, hi], color=PAL["ink2"], lw=1)
        ax.scatter(k, kp, s=MARKER * 0.8, color=PAL["s1"], edgecolor=PAL["surface"], linewidth=0.9, zorder=3)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        role = "baseline" if ml["models"][m]["baseline"] else "learned"
        ax.set_title(f"{m} ({role})\ntypical error ×{met['mae_factor']:.2f}, R² {met['r2']:.2f}", loc="left", fontsize=9.5)
        ax.set_xlabel("measured k (W/m·K)")
        _clean(ax, "both")
    np.atleast_1d(axes)[0].set_ylabel("predicted k, paper held out (W/m·K)")
    np.atleast_1d(axes)[0].text(0.13, 30, "within ×2", color=PAL["ink2"], fontsize=8.5)
    fig.tight_layout()
    return _save(fig, path)


def fig_model_comparison(ml: dict[str, Any], path: Path) -> Path:
    plt = _plt()
    order = list(reversed(ml["ranking_lopo_mae"]))
    fig, ax = plt.subplots(figsize=(8.4, 3.3))
    y = np.arange(len(order))
    for i, m in enumerate(order):
        e = ml["models"][m]
        ax.plot([e["random5"]["mae_log10"], e["lopo"]["mae_log10"]], [i, i], color=PAL["axis"], lw=2, zorder=1)
    ax.scatter([ml["models"][m]["random5"]["mae_log10"] for m in order], y, s=MARKER * 1.3, color=PAL["s1_light"],
               edgecolor=PAL["surface"], linewidth=RING, zorder=3, label="5-fold by row (leaks papers)")
    ax.scatter([ml["models"][m]["lopo"]["mae_log10"] for m in order], y, s=MARKER * 1.3, color=PAL["s1"],
               edgecolor=PAL["surface"], linewidth=RING, zorder=3, label="leave-one-paper-out (honest)")
    for i, m in enumerate(order):
        e = ml["models"][m]["lopo"]
        ax.text(e["mae_log10"] + 0.008, i, f"×{e['mae_factor']:.2f}", va="center", color=PAL["ink2"], fontsize=8.5)
    ax.set_yticks(y, [f"{m} (baseline)" if ml["models"][m]["baseline"] else m for m in order])
    ticks = [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45]
    ax.set_xticks(ticks, [f"{t:.2f}\n×{10 ** t:.2f}" for t in ticks])
    ax.set_xlim(0.12, 0.48)
    ax.set_xlabel("typical error: MAE of log10(k), with the equivalent factor")
    ax.set_title("Prediction error for unseen papers vs a leaky split", loc="left")
    ax.legend(loc="lower right")
    _clean(ax, "x")
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    return _save(fig, path)


def fig_ablation(ml: dict[str, Any], path: Path) -> Path | None:
    abl = ml.get("ablation")
    if not abl:
        return None
    plt = _plt()
    groups = list(reversed(abl["groups"]))
    fig, ax = plt.subplots(figsize=(8.4, 3.6))
    y = np.arange(len(groups))
    for i, g in enumerate(groups):
        sd = g.get("delta_sd") or 0.0
        col = PAL["s1"] if g.get("clear") else PAL["muted"]
        ax.plot([g["delta_mae"] - 2 * sd, g["delta_mae"] + 2 * sd], [i, i], color=col, lw=2, zorder=2)
    ax.scatter([g["delta_mae"] for g in groups], y, s=MARKER * 1.3,
               color=[PAL["s1"] if g.get("clear") else PAL["muted"] for g in groups],
               edgecolor=PAL["surface"], linewidth=RING, zorder=3)
    ax.axvline(0, color=PAL["ink2"], lw=1)
    ax.set_yticks(y, [g["group"] for g in groups])
    ax.set_xlabel("increase in error when the group is removed (Δ MAE log10, ±2 SD over paired repeats)")
    ax.set_title(f"Which information helps predict an unseen paper ({abl['model']})", loc="left")
    from matplotlib.lines import Line2D

    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=PAL["s1"], label="clearly helps (Δ > 2 SD)"),
                       Line2D([], [], marker="o", ls="", color=PAL["muted"], label="not distinguishable from zero")],
              loc="lower right")
    _clean(ax, "x")
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    return _save(fig, path)
