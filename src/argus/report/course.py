"""Course report: docs/course_report/COURSE_REPORT.md, rendered from results.

Every number in the report comes from the context built here, which reads the
analysis outputs (refusing stale or quick-mode ones via the dataset
fingerprint) and computes descriptive statistics live from the records.
Literature values carry citations in the template itself.
"""
from __future__ import annotations

import datetime as _dt
import json
import math
import statistics
from collections import Counter
from importlib import resources
from pathlib import Path
from typing import Any

from ..enrich import enrich_records
from ..fingerprint import StaleAnalysis, check_fresh, dataset_fingerprint
from ..io import atomic_write_text, load_yaml, read_csv
from ..paths import Layout
from ..physics.fit import build_series, fit_series
from ..records import compile_rows, load_records
from ..verify import dataset_stats
from . import figures as F

SUPERSCRIPT = str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹")


def sci(x: float, digits: int = 1) -> str:
    """6.81e-07 -> '6.8×10⁻⁷'."""
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    m = x / 10 ** e
    return f"{m:.{digits}f}×10{str(e).translate(SUPERSCRIPT)}"


def f2(x: float) -> str:
    return f"{x:.2f}"


def pct(x: float, digits: int = 0) -> str:
    return f"{100 * x:.{digits}f}%"


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise StaleAnalysis(f"{path.name} is missing")
    return json.loads(path.read_text(encoding="utf-8"))


def reporting_gaps(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """What the source papers left unstated, computed from the enriched rows."""
    n = len(rows)
    lfa = [r for r in rows if r["method_class"] == "LFA"]

    def blank(field: str) -> int:
        return sum(1 for r in rows if r[field] in ("", None))

    gaps = [
        ("Measurement direction (in-plane / through-plane)", sum(r["direction_reported"] == "unknown" for r in rows), n),
        ("Measurement technique or instrument", sum(r["method_class"] == "UNSPECIFIED" for r in rows), n),
        ("How Cp and density were obtained (laser-flash rows)",
         sum("lfa_cp_rho_unreported" in r["flags"] for r in lfa), len(lfa)),
        ("Neat-matrix k measured alongside", sum(r["k_matrix_basis"] != "reported" for r in rows), n),
        ("Filler particle size", blank("filler_mean_size_um"), n),
        ("Filler orientation or alignment", blank("filler_alignment"), n),
        ("Measurement temperature", blank("measurement_temperature_C"), n),
    ]
    return [{"item": a, "missing": m, "of": t, "share": m / t if t else 0.0} for a, m, t in gaps]


def build_context(lay: Layout, fig_dir: Path, fig_rel: str) -> dict[str, Any]:
    records = load_records(lay).records
    rows_flat = compile_rows(records)
    rows = enrich_records(records)
    fp = dataset_fingerprint(records)

    phys = _load(lay.reports / "physics_summary.json")
    bias = _load(lay.reports / "method_bias.json")
    ml = _load(lay.reports / "ml_benchmark.json")
    check_fresh("reports/physics_summary.json", phys, fp, "argus physics")
    check_fresh("reports/method_bias.json", bias, fp, "argus analyze bias")
    check_fresh("reports/ml_benchmark.json", ml, fp, "argus ml benchmark")
    if (ml.get("config") or {}).get("quick"):
        raise StaleAnalysis("reports/ml_benchmark.json came from a --quick run; re-run `argus ml benchmark`")
    pred_path = lay.reports / "ml_lopo_predictions.csv"
    pred_rows = read_csv(pred_path)
    if len(pred_rows) != ml["data"]["rows"]:
        raise StaleAnalysis("reports/ml_lopo_predictions.csv does not match ml_benchmark.json; re-run `argus ml benchmark`")

    meta = load_yaml(lay.data / "dataset.yaml") or {}
    stats = dataset_stats(rows_flat)
    fam = Counter(r["filler_family"] for r in rows)
    base = Counter(r["filler_base"] for r in rows)
    mat = Counter(r["matrix_family"] for r in rows)
    method = Counter(r["method_class"] for r in rows)
    qa_density = None
    from ..enrich import density_check

    qa_density = density_check(rows)

    # --- figures
    fits = [fit_series(s) for s in build_series(rows)]
    rk_med = phys["parameters"]["nan_R_K_m2K_W"]["median"]
    figs = {
        "overview": F.fig_overview(rows, fig_dir / "fig1_overview.png"),
        "bias": F.fig_method_bias(bias, fig_dir / "fig2_method_bias.png"),
        "loading": F.fig_k_vs_loading(rows, rk_med, fig_dir / "fig3_k_vs_loading.png"),
        "rk": F.fig_interface_resistance(fits, fig_dir / "fig4_interface_resistance.png"),
        "parity": F.fig_parity(pred_rows, ml, fig_dir / "fig5_parity.png"),
        "models": F.fig_model_comparison(ml, fig_dir / "fig6_model_comparison.png"),
        "ablation": F.fig_ablation(ml, fig_dir / "fig7_ablation.png"),
    }
    figs = {k: (f"{fig_rel}/{p.name}" if p else None) for k, p in figs.items()}

    # --- bias
    main = bias["pooled_models"]["main"]
    eff = main["effects"]
    an = bias["anisotropy"]
    films = [p["ratio"] for p in bias["direction_pairs"] if "network" not in f"{p['shape']} {p['alignment']}".lower()]
    nets = [p["ratio"] for p in bias["direction_pairs"] if "network" in f"{p['shape']} {p['alignment']}".lower()]
    sens = {k: m["effects"].get("method:MIXED") for k, m in bias["pooled_models"].items() if not m.get("skipped")}

    # --- ml
    M = ml["models"]
    best, bbase = ml["best_model"], ml["best_baseline"]
    gaps_leak = {n: M[n]["group5"]["mae_log10"] - M[n]["random5"]["mae_log10"] for n in M}
    leak_model = max(gaps_leak, key=gaps_leak.get)
    abl = ml.get("ablation") or {"groups": []}
    clear = [g for g in abl["groups"] if g.get("clear")]
    timed = {n: M[n]["time_split"]["mae_log10"] for n in M if M[n].get("time_split")}
    time_best = min(timed, key=timed.get) if timed else None

    ctx: dict[str, Any] = {
        "today": _dt.date.today().isoformat(),
        "meta": meta, "fp": fp, "stats": stats,
        "n_rows": stats["rows"], "n_papers": stats["papers"],
        "fam": fam, "base": base, "mat": mat, "method": method,
        "density": qa_density,
        "gaps": reporting_gaps(rows),
        "figs": figs,
        "an": an, "pairs": bias["direction_pairs"], "film_A": (min(films), max(films)) if films else None,
        "net_A": (min(nets), max(nets)) if nets else None,
        "main": main, "eff": eff, "sens": sens,
        "budget": bias["uncertainty_budget"],
        "n_method_pairs": len(bias["method_pairs"]),
        "phys": phys,
        "ml": ml, "M": M, "best": best, "bbase": bbase, "leak_model": leak_model,
        "leak": {"group5": M[leak_model]["group5"]["mae_log10"], "random5": M[leak_model]["random5"]["mae_log10"]},
        "abl": abl, "clear": clear, "time_best": time_best, "timed": timed,
        "ranking": ml["ranking_lopo_mae"],
    }
    return ctx


def render(lay: Layout, out: Path | None = None) -> Path:
    from jinja2 import Environment, StrictUndefined

    out = out or (lay.root / "docs" / "course_report" / "COURSE_REPORT.md")
    fig_dir = out.parent / "figures"
    ctx = build_context(lay, fig_dir, "figures")
    env = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    env.filters.update(sci=sci, f2=f2, pct=pct, median=statistics.median)
    src = resources.files("argus").joinpath("report/templates/course_report.md.j2").read_text(encoding="utf-8")
    text = env.from_string(src).render(**ctx)
    atomic_write_text(out, text)
    return out
