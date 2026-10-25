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


COMPOSITION_GROUPS = {"loading", "physics", "filler"}
GROUP_NAMES = {"direction": "measurement direction", "method": "measurement method",
               "treatment": "surface treatment", "quality": "data-quality flags"}


def ablation_summary(abl: dict[str, Any]) -> dict[str, Any]:
    """Which feature groups beyond composition clearly help, so the prose follows the numbers.

    A combined group ("direction + method") counts towards its parts only through the
    single-group rows; the combined rows can be clear just because one part is.
    """
    groups = abl.get("groups", [])
    singles = {g["group"]: g for g in groups if "+" not in g["group"]}
    meta = {n: g for n, g in singles.items() if n not in COMPOSITION_GROUPS}
    helps = sorted((n for n, g in meta.items() if g.get("clear")), key=lambda n: -meta[n]["delta_mae"])
    # metadata pairs that help together while neither part does alone
    joint = []
    for g in groups:
        parts = [p.strip() for p in g["group"].split("+")]
        if (len(parts) > 1 and g.get("clear") and not set(parts) & COMPOSITION_GROUPS
                and not any(singles.get(p, {}).get("clear") for p in parts)):
            joint.append((parts, g["delta_mae"]))
    in_joint = {p for parts, _ in joint for p in parts}
    ranked = [(GROUP_NAMES.get(n, n), meta[n]["delta_mae"]) for n in helps]
    ranked += [(" and ".join(GROUP_NAMES.get(p, p) for p in parts) + " together", d) for parts, d in joint]
    pair = next((g for g in groups if g["group"] == "loading + physics"), None)
    return {
        "meta_helps": [GROUP_NAMES.get(n, n) for n in helps],
        "meta_joint": [[GROUP_NAMES.get(p, p) for p in parts] for parts, _ in joint],
        "meta_noise": [GROUP_NAMES.get(n, n) for n in meta if n not in helps and n not in in_joint],
        "meta_top": max(ranked, key=lambda t: t[1])[0] if ranked else None,
        "direction_helps": "direction" in helps or "direction" in in_joint,
        "overlap": bool(pair and pair.get("clear")
                        and not any(singles.get(n, {}).get("clear") for n in ("loading", "physics"))),
    }


METHOD_LABEL = {
    "LFA": "laser flash", "TPS": "Hot Disk/TPS", "THB": "transient hot bridge",
    "MTPS": "modified transient plane source", "HOT_WIRE": "hot wire", "SS_D5470": "D5470-type steady state",
    "SS_GHFM": "guarded heat flow meter", "SS_HFM_GHP": "heat flow meter or guarded hot plate",
    "SS_UNSPECIFIED": "steady state, apparatus not named", "PERIODIC": "periodic heating",
    "THIN_FILM": "3ω or thermoreflectance", "IR_THERMO": "IR thermography", "UNSPECIFIED": "not stated",
}
RARE_METHOD_ROWS = 5


def method_summary(method: Counter) -> dict[str, Any]:
    """Technique classes by row count; classes under RARE_METHOD_ROWS rows are grouped together."""
    named = [(c, n) for c, n in method.most_common() if c != "UNSPECIFIED"]
    common = [(METHOD_LABEL.get(c, c), n) for c, n in named if n >= RARE_METHOD_ROWS]
    rare = [(METHOD_LABEL.get(c, c), n) for c, n in named if n < RARE_METHOD_ROWS]
    return {"common": common, "rare": rare, "rare_rows": sum(n for _, n in rare),
            "top": [label for label, _ in common[:2]], "unspecified": method.get("UNSPECIFIED", 0)}


def matrix_summary(mat: Counter) -> dict[str, Any]:
    """Epoxy, the next two named matrix families, and how many other families remain."""
    named = [(m, n) for m, n in mat.most_common() if m not in ("epoxy", "other", "")]
    return {"next": named[:2], "n_more_families": len(named[2:]), "other_rows": mat.get("other", 0)}


def acquisition_summary(records: list[Any], acq_dir: Path | None = None) -> dict[str, int]:
    """Rows and papers added by the Phase 6 acquisition (extraction-log candidate ids 'P6-…').

    figure_only counts the values the extractors saw only in figures of the papers that were
    kept (data/acquisition/extractions/*.json), which were not digitized.
    """
    p6 = [r for r in records if any(str(e.get("candidate_id", "")).startswith("P6-") for e in r.extraction_log)]
    kept = {str(r.paper.doi).lower() for r in p6}
    figure_only = 0
    for path in sorted(acq_dir.glob("*.json")) if acq_dir and acq_dir.is_dir() else []:
        for paper in json.loads(path.read_text(encoding="utf-8")).get("papers", []):
            n = paper.get("figure_only_skipped") or 0
            if str(paper.get("doi", "")).lower() in kept and isinstance(n, int):
                figure_only += n
    return {"papers": len(p6), "rows": sum(len(r.measurements) for r in p6), "figure_only": figure_only}


def andjoin(items: list[Any]) -> str:
    """['a', 'b', 'c'] -> 'a, b and c'."""
    items = [str(i) for i in items]
    return " and ".join([", ".join(items[:-1]), items[-1]]) if len(items) > 1 else "".join(items)


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
    ext = None
    ext_path = lay.reports / "external_validation.json"
    if ext_path.exists():
        ext = _load(ext_path)
        check_fresh("reports/external_validation.json", ext, fp, "argus external validate")
        if (ext.get("config") or {}).get("quick"):
            raise StaleAnalysis("reports/external_validation.json came from a --quick run; re-run `argus external validate`")
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
    unspec = {k: m["effects"].get("method:UNSPECIFIED") for k, m in bias["pooled_models"].items() if not m.get("skipped")}

    # --- ml
    M = ml["models"]
    best, bbase = ml["best_model"], ml["best_baseline"]
    gaps_leak = {n: M[n]["group5"]["mae_log10"] - M[n]["random5"]["mae_log10"] for n in M}
    leak_model = max(gaps_leak, key=gaps_leak.get)
    abl = ml.get("ablation") or {"groups": []}
    clear = [g for g in abl["groups"] if g.get("clear")]
    timed = {n: M[n]["time_split"]["mae_log10"] for n in M if M[n].get("time_split")}
    time_best = min(timed, key=timed.get) if timed else None

    from ..release import author_names, citation_text

    ctx: dict[str, Any] = {
        "today": _dt.date.today().isoformat(),
        "authors": author_names(meta), "citation": citation_text(meta),
        "meta": meta, "fp": fp, "stats": stats,
        "n_rows": stats["rows"], "n_papers": stats["papers"],
        "fam": fam, "base": base, "mat": mat, "method": method,
        "methods": method_summary(method), "mats": matrix_summary(mat), "acq": acquisition_summary(records, lay.data / "acquisition" / "extractions"),
        "density": qa_density,
        "gaps": reporting_gaps(rows),
        "figs": figs,
        "an": an, "pairs": bias["direction_pairs"], "film_A": (min(films), max(films)) if films else None,
        "net_A": (min(nets), max(nets)) if nets else None,
        "main": main, "eff": eff, "sens": sens, "unspec": unspec,
        "budget": bias["uncertainty_budget"],
        "n_method_pairs": len(bias["method_pairs"]),
        "phys": phys,
        "ml": ml, "M": M, "best": best, "bbase": bbase, "leak_model": leak_model,
        "leak": {"group5": M[leak_model]["group5"]["mae_log10"], "random5": M[leak_model]["random5"]["mae_log10"]},
        "abl": abl, "clear": clear, "abls": ablation_summary(abl), "time_best": time_best, "timed": timed,
        "ranking": ml["ranking_lopo_mae"],
        "best_phrase": MODEL_PHRASE.get(best, best),
        "ext": external_context(ext, figs_ext(lay, fig_dir, fig_rel)) if ext else None,
    }
    return ctx


MODEL_PHRASE = {
    "xgboost": "gradient boosting constrained so that predicted *k* never falls as loading rises",
    "ensemble": "an equal-weight ensemble of calibrated physics with a Gaussian-process correction, ridge "
                "regression and monotone gradient boosting",
    "gp_residual": "calibrated physics with a Gaussian-process correction",
    "random_forest": "a random forest",
    "ridge": "ridge regression",
}
MODEL_LABEL = {"physics": "calibrated physics (baseline)", "gp_residual": "physics + Gaussian process",
               "ensemble": "ensemble", "xgboost": "gradient boosting", "ridge": "ridge", "random_forest": "random forest",
               "knn": "nearest neighbours (baseline)", "median": "median (baseline)"}


def figs_ext(lay: Layout, fig_dir: Path, fig_rel: str) -> dict[str, str]:
    """Copy the external-validation figures next to the report's own figures."""
    import shutil

    out = {}
    transfer = "external_transfer_all.png"
    if not (lay.reports / "figures" / transfer).exists():
        transfer = "external_transfer_evf.png"
    for name in (transfer, "external_bcc_models.png"):
        src = lay.reports / "figures" / name
        if src.exists():
            fig_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, fig_dir / name)
            out[name.removeprefix("external_").removesuffix(".png")] = f"{fig_rel}/{name}"
    return out


def _crosscheck_summary(ext: dict[str, Any]) -> dict[str, Any] | None:
    cc = [c for c in (ext.get("crosscheck") or {}).values() if c["shared_papers"]]
    if not cc:
        return None
    grades = Counter(p["grade"] for c in cc for p in c["pair_rows"])
    rv = ext.get("crosscheck_review") or {}
    review = rv.get("papers") or {}
    return {"papers": len({d for c in cc for d in c["shared_dois"]}),
            "pairs": sum(c["pairs"] for c in cc), "agree": grades.get("agree", 0),
            "minor": grades.get("minor", 0), "disagree": grades.get("disagree", 0),
            "unmatched": sum(len(c["unmatched_external"]) for c in cc), "review": review,
            "unreviewed": rv.get("unreviewed") or [],
            "no_change": bool(review) and all(str(v.get("action", "")).strip().lower().startswith("none")
                                              for v in review.values())}


def external_context(ext: dict[str, Any], figs: dict[str, str]) -> dict[str, Any]:
    """Pre-digested numbers for Section 4.5, so the template stays readable."""
    pc = ext.get("physics_check", {})
    compared = [(src, m, s) for src, chk in pc.items() for m, s in chk.items()
                if isinstance(s, dict) and "n_exact" in s]
    exact = [(src, m, s) for src, m, s in compared if s["n_exact"] == s["n"]]
    key = "all" if "all" in ext["transfer"] else next(iter(ext["transfer"]), None)
    t = ext["transfer"].get(key) if key else None
    rows = []
    if t:
        for m in t["ranking_test_mae"]:
            e = t["models"][m]
            vs = e.get("vs_reference")
            rows.append({"model": m, "label": MODEL_LABEL.get(m, m), "factor": e["test"]["mae_factor"],
                         "mae": e["test"]["mae_log10"], "ci": e["test_mae_ci95"],
                         "ci_factor": ((10 ** e["test_mae_ci95"][0], 10 ** e["test_mae_ci95"][1])
                                       if e["test_mae_ci95"] else None),
                         "vs": vs, "coverage": e["interval"]["coverage"], "lopo": e["train_lopo_mae"],
                         "in": (e.get("in_domain") or {}).get("mae_log10"), "out": (e.get("out_of_domain") or {}).get("mae_log10")})
    clearly_better = [r["label"] for r in rows if r["vs"] and r["vs"]["clear"] and r["vs"]["mae_diff"] < 0]
    clearly_worse = [r["label"] for r in rows if r["vs"] and r["vs"]["clear"] and r["vs"]["mae_diff"] > 0
                     and r["model"] not in ("median", "knn")]
    pooled = (ext.get("pooled") or {}).get(key) or next(iter((ext.get("pooled") or {}).values()), None)
    clear_pooled = [m for m, e in (pooled or {}).get("models", {}).items()
                    if e["train_rows"]["ci95"] and e["train_rows"]["ci95"][1] < 0]
    cc = {k: c for k, c in (ext.get("crosscheck") or {}).items() if c["shared_papers"]}
    by_model = {r["model"]: r for r in rows}
    learned = [r for r in rows if r["model"] not in ("median", "physics", "knn")]
    top = learned[0] if learned else None
    cov_ok = [r for r in learned if r["coverage"] >= 0.9]
    under = [r for r in learned if r["coverage"] < 0.9]
    pooled_detail = []
    for m in clear_pooled:
        e = pooled["models"][m]["train_rows"]
        pooled_detail.append({"label": MODEL_LABEL.get(m, m), "alone": e["alone_lopo"], "pooled": e["pooled_lopo"],
                              "ci": e["ci95"]})
    pooled_ext_clear = [MODEL_LABEL.get(m, m) for m, e in (pooled or {}).get("models", {}).items()
                        if e["external_rows"]["ci95"] and e["external_rows"]["ci95"][1] < 0]
    return {
        "sources": ext["sources"], "key": key, "test": t["test"] if t else None, "rows": rows, "by": by_model,
        "domain": (t or {}).get("domain") or {"new_fillers": [], "new_matrices": [], "sources": []},
        "code": {"n_models": len(compared), "n_exact": len(exact),
                 "points": sum(s["n"] for _, _, s in compared),
                 "points_exact": sum(s["n"] for _, _, s in exact), "sources": sorted(pc)},
        "cc": _crosscheck_summary(ext),
        "dem": pc.get("bcc", {}).get("bruggeman_dem"),
        "bcc": ext.get("physics_on_bcc"), "pooled": pooled,
        "pooled_clear": [MODEL_LABEL.get(m, m) for m in clear_pooled],
        # largest change among the models whose change is NOT clearly non-zero
        "pooled_max_abs": (max((abs(e["train_rows"]["diff"]) for m, e in pooled["models"].items() if m not in clear_pooled),
                               default=0.0) if pooled else None),
        "tested": {k: v["test"] for k, v in (ext.get("transfer") or {}).items() if k != "all"},
        "top": top, "phys": by_model.get("physics"),
        "cov_ok": [r["label"] for r in cov_ok],
        "cov_ok_min": min((r["coverage"] for r in cov_ok), default=None),
        "cov_ok_max": max((r["coverage"] for r in cov_ok), default=None),
        "under_cover": [{"label": r["label"], "coverage": r["coverage"]} for r in under],
        "pooled_detail": pooled_detail, "pooled_ext_clear": pooled_ext_clear,
        "coverage_min": min((r["coverage"] for r in rows if r["model"] not in ("median", "knn")), default=None),
        "clearly_better": clearly_better, "clearly_worse": clearly_worse,
        "crosscheck": cc, "figs": figs,
    }


def render(lay: Layout, out: Path | None = None) -> Path:
    from jinja2 import Environment, StrictUndefined

    out = out or (lay.root / "docs" / "course_report" / "COURSE_REPORT.md")
    fig_dir = out.parent / "figures"
    ctx = build_context(lay, fig_dir, "figures")
    env = Environment(undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    env.filters.update(sci=sci, f2=f2, pct=pct, median=statistics.median, andjoin=andjoin)
    src = resources.files("argus").joinpath("report/templates/course_report.md.j2").read_text(encoding="utf-8")
    text = env.from_string(src).render(**ctx)
    atomic_write_text(out, text)
    return out
