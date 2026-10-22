"""Phase 4: how much do measurement technique and direction shift reported k?

Three kinds of evidence, strongest first:

1. Same-sample pairs. The same sample (same paper, composition, processing and
   loading) reported in two directions or by two methods. These isolate the
   effect directly.
2. Anisotropy -> expected method bias. An isotropic-mode transient sensor (TPS,
   THB, hot wire) on a sample with anisotropy A = k_in/k_through reads about
   sqrt(k_in k_through), i.e. sqrt(A) times the through-plane value that laser
   flash on a disc reports (research report, measurement section).
3. A pooled between-paper model of log10(k/k_m) for BN-platelet composites,
   with a random intercept per paper. Method effects here are associations:
   most papers use one technique, so method is confounded with everything else
   that differs between papers.

Read-only: works on the enriched rows, never on records.
"""
from __future__ import annotations

import math
import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any, Iterable

import numpy as np

from .lmm import fit_lmm, fit_ols

METHOD_GROUP = {
    "LFA": "LFA",
    "TPS": "MIXED", "THB": "MIXED", "HOT_WIRE": "MIXED", "MTPS": "MIXED",
    "SS_D5470": "STEADY", "SS_GHFM": "STEADY", "SS_HFM_GHP": "STEADY", "SS_UNSPECIFIED": "STEADY",
    "PERIODIC": "OTHER", "THIN_FILM": "OTHER", "IR_THERMO": "OTHER",
    "UNSPECIFIED": "UNSPECIFIED",
}
GROUP_LABEL = {
    "LFA": "laser flash (through-plane on discs)",
    "MIXED": "isotropic-mode transient sensors (TPS, THB, hot wire)",
    "STEADY": "steady-state heat flow (D5470-type, guarded heat flow)",
    "OTHER": "periodic / IR methods",
    "UNSPECIFIED": "method not stated",
}
BN_PLATELET = frozenset({"h-BN", "BN", "BNNS"})
SAMPLE_KEY = ("doi", "matrix_polymer", "curing_agent", "filler_material", "filler_shape", "filler_mean_size_um",
              "functionalization", "filler_alignment", "processing_method", "measurement_temperature_C",
              "filler_loading_vol_pct", "filler_loading_wt_pct", "filler_loading_original_value")
DIGITIZATION_PX = 1.0  # centroid uncertainty assumed for pixel-digitized markers, in pixels
_RES = re.compile(r"resolution\s*~?\s*([0-9.]+)\s*W/m\s*K\s*per\s*px", re.IGNORECASE)


def _f(v: Any) -> float | None:
    if isinstance(v, bool) or v is None or v == "":
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _sig(x: float | None, n: int = 3) -> float | None:
    return None if x is None else float(f"{x:.{n}g}")


# --------------------------------------------------------------------------- 1. same-sample pairs

@dataclass
class Pair:
    paper_id: str
    doi: str
    filler: str
    shape: str
    alignment: str
    phi_vol_pct: float | None
    a_label: str
    b_label: str
    k_a: float
    k_b: float

    @property
    def ratio(self) -> float:
        return self.k_a / self.k_b


def _groups(rows: Iterable[dict[str, Any]]) -> dict[tuple, list[dict[str, Any]]]:
    g: dict[tuple, list[dict[str, Any]]] = defaultdict(list)
    for r in rows:
        g[tuple(str(r.get(c, "")) for c in SAMPLE_KEY)].append(r)
    return g


def direction_pairs(rows: Iterable[dict[str, Any]]) -> list[Pair]:
    """Same sample reported in-plane AND through-plane (a = in-plane, b = through-plane)."""
    out = []
    for g in _groups(rows).values():
        ins = [r for r in g if r["direction_reported"] == "in-plane"]
        thr = [r for r in g if r["direction_reported"] == "through-plane"]
        for a, b in zip(ins, thr):
            out.append(Pair(a["paper_id"], a["doi"], a["filler_material"], a["filler_shape"], a["filler_alignment"],
                            _f(a["phi_vol_pct"]), "in-plane", "through-plane",
                            float(a["k_composite_W_mK"]), float(b["k_composite_W_mK"])))
    return sorted(out, key=lambda p: (p.paper_id, p.phi_vol_pct or 0))


def method_pairs(rows: Iterable[dict[str, Any]]) -> list[Pair]:
    """Same sample and direction measured by two named method classes."""
    out = []
    for g in _groups(rows).values():
        named = [r for r in g if r["method_class"] != "UNSPECIFIED"]
        for i, a in enumerate(named):
            for b in named[i + 1:]:
                if a["method_class"] != b["method_class"] and a["direction_reported"] == b["direction_reported"]:
                    out.append(Pair(a["paper_id"], a["doi"], a["filler_material"], a["filler_shape"],
                                    a["filler_alignment"], _f(a["phi_vol_pct"]), a["method_class"],
                                    b["method_class"], float(a["k_composite_W_mK"]), float(b["k_composite_W_mK"])))
    return out


def anisotropy_summary(pairs: list[Pair]) -> dict[str, Any]:
    """A = k_in/k_through and the method bias it implies for isotropic-mode sensors."""
    if not pairs:
        return {"n_pairs": 0}
    ratios = [p.ratio for p in pairs]
    med = statistics.median(ratios)
    return {
        "n_pairs": len(pairs),
        "papers": sorted({p.paper_id for p in pairs}),
        "A_median": _sig(med), "A_min": _sig(min(ratios)), "A_max": _sig(max(ratios)),
        "implied_isotropic_sensor_over_through_plane": {
            "at_A_median": _sig(math.sqrt(med)), "at_A_min": _sig(math.sqrt(min(ratios))),
            "at_A_max": _sig(math.sqrt(max(ratios))),
            "basis": "k_TPS ~ sqrt(k_in k_through) => k_TPS / k_through = sqrt(A)",
        },
    }


# --------------------------------------------------------------------------- 2. pooled model

@dataclass
class ModelSpec:
    name: str
    description: str
    exclude_flags: tuple[str, ...] = ()
    require_reported_km: bool = False


SPECS = (
    ModelSpec("main", "All single-filler BN-platelet rows with a loading"),
    ModelSpec("printed_only", "Excluding abstract-only and figure-digitized rows",
              exclude_flags=("abstract_only", "figure_digitized")),
    ModelSpec("reported_km", "Only rows whose paper reports the neat-matrix k", require_reported_km=True),
)


def model_rows(rows: Iterable[dict[str, Any]], spec: ModelSpec) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        phi, km, k = _f(r["phi_vol_pct"]), _f(r["k_matrix_effective"]), _f(r["k_composite_W_mK"])
        if r["filler_base"] not in BN_PLATELET or r["is_hybrid"] in (True, "true") or not phi or not km or not k:
            continue
        flags = set(str(r["flags"]).split(";"))
        if flags & set(spec.exclude_flags):
            continue
        if spec.require_reported_km and r["k_matrix_basis"] != "reported":
            continue
        out.append(r)
    return out


def design(rows: list[dict[str, Any]]) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    groups_present = [g for g in ("MIXED", "STEADY", "OTHER", "UNSPECIFIED")
                      if any(METHOD_GROUP[r["method_class"]] == g for r in rows)]
    names = ["intercept", "phi", "phi^2", "BNNS", "in_plane"] + [f"method:{g}" for g in groups_present]
    X, y, grp = [], [], []
    for r in rows:
        phi = _f(r["phi_vol_pct"]) / 100.0
        mg = METHOD_GROUP[r["method_class"]]
        X.append([1.0, phi, phi * phi, float(r["filler_base"] == "BNNS"), float(r["direction_reported"] == "in-plane")]
                 + [float(mg == g) for g in groups_present])
        y.append(math.log10(float(r["k_composite_W_mK"]) / _f(r["k_matrix_effective"])))
        grp.append(r["paper_id"])
    X_arr = np.array(X)
    keep = [j for j in range(X_arr.shape[1]) if j == 0 or np.ptp(X_arr[:, j]) > 0]  # drop constant columns
    return np.array(y), X_arr[:, keep], np.array(grp), [names[j] for j in keep]


def pooled_model(rows: Iterable[dict[str, Any]], spec: ModelSpec = SPECS[0]) -> dict[str, Any]:
    sel = model_rows(rows, spec)
    if len(sel) < 10:
        return {"spec": spec.name, "n": len(sel), "skipped": "too few rows"}
    y, X, grp, names = design(sel)
    fit = fit_lmm(y, X, grp, names)
    ols = fit_ols(y, X, names)
    papers_per_group = Counter()
    rows_per_group = Counter()
    seen = set()
    for r in sel:
        g = METHOD_GROUP[r["method_class"]]
        rows_per_group[g] += 1
        if (g, r["paper_id"]) not in seen:
            seen.add((g, r["paper_id"]))
            papers_per_group[g] += 1
    effects = {}
    for n in names:
        if n.startswith("method:") or n in ("in_plane", "BNNS"):
            c = fit.coef(n)
            g = n.split(":", 1)[1] if n.startswith("method:") else None
            effects[n] = {
                "factor": _sig(10 ** c["beta"]), "ci95": [_sig(10 ** c["ci_low"]), _sig(10 ** c["ci_high"])],
                "beta_log10": _sig(c["beta"], 4), "se_log10": _sig(c["se"], 3), "df": c["df"],
                "between_paper_contrast": c["between_group"],
                "papers": papers_per_group.get(g) if g else None, "rows": rows_per_group.get(g) if g else None,
                "naive_ols_factor": _sig(10 ** ols[n]["beta"]),
                "naive_ols_ci95": [_sig(10 ** ols[n]["ci_low"]), _sig(10 ** ols[n]["ci_high"])],
            }
    return {
        "spec": spec.name, "description": spec.description, "n": fit.n, "papers": fit.groups,
        "response": "log10(k / k_matrix_effective)",
        "reference": "laser flash (LFA), h-BN/BN, direction not in-plane",
        "covariates": names,
        "rows_per_method_group": dict(rows_per_group), "papers_per_method_group": dict(papers_per_group),
        "effects": effects,
        "between_paper_sd_log10": _sig(math.sqrt(fit.tau2)), "within_paper_sd_log10": _sig(math.sqrt(fit.sigma2)),
        "between_paper_factor_1sd": _sig(10 ** math.sqrt(fit.tau2)),
        "icc": _sig(fit.icc),
    }


# --------------------------------------------------------------------------- 3. uncertainty budget

def digitization_resolution(rows: list[dict[str, Any]]) -> dict[str, float]:
    """W/(m K) per pixel for each paper with figure rows (from the row notes)."""
    per_paper: dict[str, list[float]] = defaultdict(list)
    for r in rows:
        if r["value_source"] == "figure" and (m := _RES.search(str(r["notes"]))):
            per_paper[r["paper_id"]].append(float(m.group(1)))
    return {p: statistics.median(v) for p, v in per_paper.items()}


def uncertainty_rows(rows: list[dict[str, Any]], fallback_res: float = 0.02) -> list[dict[str, Any]]:
    res = digitization_resolution(rows)
    out = []
    for r in rows:
        k = float(r["k_composite_W_mK"])
        s_m = float(r["k_rel_uncertainty"])
        s_d = 0.0
        if r["value_source"] == "figure":
            m = _RES.search(str(r["notes"]))
            px = float(m.group(1)) if m else res.get(r["paper_id"], fallback_res)
            s_d = DIGITIZATION_PX * px / k
        out.append({"row_id": r["row_id"], "paper_id": r["paper_id"], "method_class": r["method_class"],
                    "rel_sigma_method": s_m, "rel_sigma_digitization": round(s_d, 4),
                    "rel_sigma_total": round(math.hypot(s_m, s_d), 4)})
    return out


def uncertainty_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    u = uncertainty_rows(rows)
    by: dict[str, list[float]] = defaultdict(list)
    for x in u:
        by[x["method_class"]].append(x["rel_sigma_total"])
    dig = [x["rel_sigma_digitization"] for x in u if x["rel_sigma_digitization"] > 0]
    return {
        "rows": len(u),
        "median_rel_sigma_by_method": {m: _sig(statistics.median(v)) for m, v in sorted(by.items())},
        "figure_rows": len(dig),
        "figure_digitization_rel_sigma_median": _sig(statistics.median(dig)) if dig else None,
        "figure_digitization_rel_sigma_max": _sig(max(dig)) if dig else None,
        "median_rel_sigma_all": _sig(statistics.median(x["rel_sigma_total"] for x in u)),
        "assumptions": f"method sigma = judgement default per class (vocab.METHOD_CLASSES); digitization sigma = "
                       f"{DIGITIZATION_PX:g} px x axis resolution / k",
    }


# --------------------------------------------------------------------------- 4. assemble

LITERATURE = [
    ("PMMA, 5-method interlaboratory study", "spread about +/-10%; TPS about +6%", "Rides et al., Polym. Test. 2009"),
    ("BN-type compounds, Hot Disk vs laser flash", "+15-20% (isotropic fillers), up to +50% (platelets)", "patent US10328620"),
    ("Filled TIMs, ASTM D5470 vs TPS", "D5470 much higher, one > 2x", "ORNL/Delphi/GM, OSTI 1570138"),
    ("Vendor instrument accuracy", "+/-3-5% (LFA diffusivity, TPS, THB)", "NETZSCH, Hot Disk, Linseis data sheets"),
]


def analyze(rows: list[dict[str, Any]]) -> dict[str, Any]:
    dp = direction_pairs(rows)
    mp = method_pairs(rows)
    models = {s.name: pooled_model(rows, s) for s in SPECS}
    main = models["main"]
    budget = uncertainty_summary(rows)
    return {
        "question": "How much do measurement technique and direction shift reported k for BN/epoxy composites?",
        "direction_pairs": [dict(asdict(p), ratio=_sig(p.ratio)) for p in dp],
        "anisotropy": anisotropy_summary(dp),
        "method_pairs": [dict(asdict(p), ratio=_sig(p.ratio)) for p in mp],
        "pooled_models": models,
        "uncertainty_budget": budget,
        "scale_comparison": {
            "instrument_rel_sigma_median": budget["median_rel_sigma_all"],
            "between_paper_factor_1sd": main.get("between_paper_factor_1sd"),
            "within_paper_sd_log10": main.get("within_paper_sd_log10"),
        },
        "literature": [{"comparison": a, "difference": b, "source": c} for a, b, c in LITERATURE],
    }


def _fmt_factor(e: dict[str, Any]) -> str:
    lo, hi = e["ci95"]
    return f"{e['factor']:.2f} ({lo:.2f}–{hi:.2f})"


def render_markdown(res: dict[str, Any]) -> str:
    an = res["anisotropy"]
    main = res["pooled_models"]["main"]
    L: list[str] = []
    L += ["# Measurement-technique bias in the ARGUS dataset", "",
          "_Generated by `argus analyze bias` from `data/processed/measurements_enriched.csv`. "
          "Read-only analysis; no record was changed._", ""]

    implied = an.get("implied_isotropic_sensor_over_through_plane", {})
    mixed = main.get("effects", {}).get("method:MIXED")
    L += ["## Summary", ""]
    if an.get("n_pairs"):
        L.append(f"- **Same-sample anisotropy is large.** {an['n_pairs']} samples were reported in both directions "
                 f"({', '.join(an['papers'])}): k_in/k_through has median {an['A_median']:.1f} "
                 f"(range {an['A_min']:.2f}–{an['A_max']:.1f}).")
        L.append(f"- **So the method alone can change k by up to ~{implied['at_A_max']:.1f}×.** An isotropic-mode "
                 f"Hot Disk / hot bridge reads ≈ √(k_in·k_through): {implied['at_A_median']:.1f}× the laser-flash "
                 f"through-plane value at the median anisotropy (range {implied['at_A_min']:.1f}–{implied['at_A_max']:.1f}×).")
    L.append(f"- **No sample in the dataset was measured by two different techniques** "
             f"({len(res['method_pairs'])} same-sample method pairs), so the direct method effect cannot be "
             "measured from this literature; only between-paper associations can.")
    if mixed:
        lo, hi = mixed["ci95"]
        verdict = ("the 95% interval includes 1, so the data are consistent with no effect as well as with the "
                   "physically expected one" if lo <= 1 <= hi else "the 95% interval excludes 1")
        L.append(f"- **Between papers**, isotropic-mode transient sensors report {_fmt_factor(mixed)}× the k of "
                 f"laser flash at the same loading (BN platelets; {mixed['papers']} vs "
                 f"{main['papers_per_method_group'].get('LFA', 0)} papers): {verdict}. A naive regression that "
                 f"treats rows as independent would give {mixed['naive_ols_factor']:.2f} "
                 f"({mixed['naive_ols_ci95'][0]:.2f}–{mixed['naive_ols_ci95'][1]:.2f}), overstating certainty.")
    sc = res["scale_comparison"]
    L.append(f"- **Paper-to-paper scatter dwarfs instrument precision.** After loading, filler and method, papers "
             f"differ by a factor of {sc['between_paper_factor_1sd']:.2f} (1 SD) while instrument uncertainty is "
             f"~{100 * sc['instrument_rel_sigma_median']:.0f}% (median judgement default). Sample preparation, "
             "filler grade and orientation, not instrument precision, dominate.")
    L.append("")

    L += ["## 1. Same-sample evidence", "", "### Direction pairs (same sample, same loading)", "",
          "| Paper | Filler | Shape / alignment | vol% | k in-plane (W/m·K) | k through-plane (W/m·K) | A = k_in/k_through |",
          "|---|---|---|---|---|---|---|"]
    for p in res["direction_pairs"]:
        phi = "" if p["phi_vol_pct"] is None else f"{p['phi_vol_pct']:.2f}"
        sa = " / ".join(x for x in (p["shape"], p["alignment"]) if x)
        L.append(f"| {p['paper_id']} | {p['filler']} | {sa} | {phi} | {p['k_a']:g} | {p['k_b']:g} | {p['ratio']:.2f} |")
    nets = [p["ratio"] for p in res["direction_pairs"] if "network" in f"{p['shape']} {p['alignment']}".lower()]
    films = [p["ratio"] for p in res["direction_pairs"] if "network" not in f"{p['shape']} {p['alignment']}".lower()]
    parts = []
    if films:
        parts.append(f"sheet/film-like samples A = {min(films):.2f}–{max(films):.2f}")
    if nets:
        parts.append(f"3D network samples A = {min(nets):.2f}–{max(nets):.2f}")
    L += ["", ("By structure: " + "; ".join(parts) + ". ") if parts else "",
          "A below 1 means the sample conducts better through-plane (e.g. a vertically built network).", "",
          "### Method pairs", "",
          f"{len(res['method_pairs'])} found. Papers in this dataset report each sample with one technique. "
          "Measuring a subset of samples by laser flash *and* Hot Disk (both modes) would settle the question "
          "directly; this is the most valuable experiment the analysis points to.", ""]

    L += ["## 2. Pooled between-paper model", "",
          f"Linear mixed model of `{main.get('response')}` with fixed effects for loading (φ, φ²), BNNS vs h-BN/BN, "
          "in-plane reporting and method group, and a random intercept per paper (REML; between/within degrees "
          "of freedom, so paper-level contrasts are judged against the number of papers).", "",
          f"Main fit: {main.get('n')} rows from {main.get('papers')} papers. Reference: {main.get('reference')}.", "",
          "| Effect | Factor on k (95% CI) | Papers | Rows | Naive OLS (ignores papers) |", "|---|---|---|---|---|"]
    label = {"in_plane": "reported in-plane", "BNNS": "BNNS vs h-BN/BN"}
    for n, e in main.get("effects", {}).items():
        g = n.split(":", 1)[1] if n.startswith("method:") else None
        name = GROUP_LABEL.get(g, g) if g else label.get(n, n)
        lo, hi = e["naive_ols_ci95"]
        L.append(f"| {name} | {_fmt_factor(e)} | {e['papers'] or ''} | {e['rows'] or ''} | "
                 f"{e['naive_ols_factor']:.2f} ({lo:.2f}–{hi:.2f}) |")
    L += ["", f"Between-paper SD {main.get('between_paper_sd_log10')} log10 (factor {main.get('between_paper_factor_1sd')}), "
          f"within-paper SD {main.get('within_paper_sd_log10')} log10; intraclass correlation {main.get('icc')}.", "",
          "The naive OLS intervals are much narrower because they treat rows from one paper as independent; "
          "they are shown only to illustrate that error.", "", "### Sensitivity", "",
          "| Fit | Rows / papers | Isotropic-mode sensors vs LFA | Steady-state vs LFA | Not stated vs LFA |",
          "|---|---|---|---|---|"]
    for name, m in res["pooled_models"].items():
        if m.get("skipped"):
            L.append(f"| {name} | {m['n']} | skipped ({m['skipped']}) | | |")
            continue
        cell = lambda key: _fmt_factor(m["effects"][key]) if key in m["effects"] else "n/a"  # noqa: E731
        L.append(f"| {m['description']} | {m['n']} / {m['papers']} | {cell('method:MIXED')} | "
                 f"{cell('method:STEADY')} | {cell('method:UNSPECIFIED')} |")
    po = res["pooled_models"].get("printed_only", {})
    u_main = main.get("effects", {}).get("method:UNSPECIFIED")
    u_po = po.get("effects", {}).get("method:UNSPECIFIED") if not po.get("skipped") else None
    if u_main and u_po and u_po["factor"] < u_main["factor"]:
        L += ["", f"The 'method not stated' group falls from {u_main['factor']:.2f} to {u_po['factor']:.2f} when "
              f"abstract-only and figure-digitized rows are excluded ({u_main['rows'] - u_po['rows']} of its "
              f"{u_main['rows']} rows drop out). Abstracts tend to quote a paper's best result, so abstract-only "
              "rows are likely biased upward and analyses should weight or exclude them."]

    ub = res["uncertainty_budget"]
    L += ["", "## 3. Uncertainty budget", "",
          f"Per-row relative σ ({ub['assumptions']}).", "",
          "| Method class | Median relative σ |", "|---|---|"]
    for m, s in ub["median_rel_sigma_by_method"].items():
        L.append(f"| {m} | {100 * s:.0f}% |")
    if ub["figure_rows"]:
        L += ["", f"Figure-digitized rows ({ub['figure_rows']}): digitization adds a median "
              f"{100 * ub['figure_digitization_rel_sigma_median']:.1f}% (max {100 * ub['figure_digitization_rel_sigma_max']:.1f}%), "
              "small next to the method default. Systematic direction error (section 1) is not included and is larger."]

    L += ["", "## 4. Comparison with published method comparisons", "",
          "| Comparison | Reported difference | Source |", "|---|---|---|"]
    for x in res["literature"]:
        L.append(f"| {x['comparison']} | {x['difference']} | {x['source']} |")
    if implied:
        L += ["", f"The dataset's own anisotropy ratios predict isotropic-sensor readings "
              f"{implied['at_A_min']:.2f}–{implied['at_A_max']:.2f}× the through-plane value. That is the same "
              "direction as the published comparisons and, for strongly anisotropic film-like samples, larger than "
              "the patent's 'up to +50%'. Sources: docs/reports/BN epoxy thermal conductivity research.md.", ""]
    L += [
          "## 5. Caveats", "",
          "- Method effects in section 2 are between-paper associations, not causal estimates: each paper also "
          "differs in filler grade, dispersion, curing and sample geometry.",
          "- 'Isotropic-mode sensors' groups TPS, THB and hot wire; whether each paper used an anisotropic module "
          "is rarely stated.",
          "- Loading is partly converted from wt% with reference densities (`phi_basis`); k_m is a family default "
          "where not reported (`k_matrix_basis`). The `reported_km` fit checks the latter.",
          "- Default uncertainties are judgement values from the research report, not standards.", ""]
    return "\n".join(L)
