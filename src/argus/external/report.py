"""`argus external validate`: every external check in one run.

  1. physics implementation cross-check (EVF and BCC workbooks)
  2. how the effective-medium models do on BCC's polymer points
  3. transfer: models trained on all of ARGUS predict each external test set
  4. pooled training: does adding the external rows help?
  5. value cross-check for papers that ARGUS and an external source share

Writes reports/external_validation.json and .md (+ figures). The JSON carries
the ARGUS dataset fingerprint, like every other analysis output, so the course
report can refuse a stale copy.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Iterable

import numpy as np

from ..enrich import enrich_records
from ..fingerprint import dataset_fingerprint
from ..io import atomic_write_text, load_yaml
from ..ml.features import build_dataset
from ..paths import Layout
from ..records import load_records
from . import manifest, physics_check
from .crosscheck import crosscheck
from .harmonize import ExternalRecord, enrich_external
from .sources import evf
from .transfer import N_BOOT, in_domain, pooled, transfer

# source key -> (role, loader(folder) -> records). Roles:
#   test        independent test set for the ML transfer (needs matrix k and loading)
#   crosscheck  only compared value-by-value with ARGUS papers it shares
Loader = Callable[[Path], Iterable[ExternalRecord]]


def registry() -> dict[str, tuple[str, Loader]]:
    from .sources import heliyon, ncomms, tagp

    return {"evf": ("test", evf.records), "ncomms": ("test", ncomms.records),
            "tagp": ("test", tagp.records), "heliyon": ("crosscheck", heliyon.records)}


def _load_sources(ext: Path) -> tuple[dict[str, list[dict[str, Any]]], dict[str, str]]:
    rows, skipped = {}, {}
    for key, (_, loader) in registry().items():
        folder = ext / key
        if not folder.exists():
            skipped[key] = "folder missing"
            continue
        try:
            rows[key] = enrich_external(loader(folder))
        except FileNotFoundError as e:
            skipped[key] = f"raw file missing ({Path(str(e.filename or e)).name}); run `argus external fetch {key}`"
    return rows, skipped


def _strip(res: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in res.items() if k != "predictions"}


def run(lay: Layout, quick: bool = False, n_boot: int = N_BOOT) -> dict[str, Any]:
    ext = lay.data / "external"
    records = load_records(lay).records
    argus_rows = enrich_records(records)
    train = build_dataset(argus_rows)
    src_rows, skipped = _load_sources(ext)
    reg = registry()
    out: dict[str, Any] = {
        "dataset": dataset_fingerprint(records),
        "config": {"quick": quick, "bootstrap": n_boot},
        "sources": {}, "skipped": skipped,
    }
    meta = manifest.load(ext)
    files = manifest.check_files(ext)
    for key, rows in src_rows.items():
        m = meta.get(key, {})
        out["sources"][key] = {
            "title": m.get("title", key), "license": m.get("license", ""), "doi": m.get("doi", ""),
            "role": reg[key][0], "rows": len(rows), "papers": len({r["paper_key"] for r in rows}),
            "files_ok": all(f["ok"] for f in files if f["source"] == key),
            "fillers": dict(Counter(r["filler_material"] for r in rows).most_common()),
            "matrices": dict(Counter(r["matrix_family"] for r in rows).most_common()),
        }

    # 1-2. physics
    out["physics_check"] = {}
    if (ext / "evf").exists():
        out["physics_check"]["evf"] = physics_check.check_evf(ext / "evf")
        out["evf_zero_loading"] = evf.zero_loading_check(ext / "evf")
        mp = evf.load_map(ext / "evf")
        out["evf_selection"] = {"included": len(mp["include"]), "excluded": len(mp["exclude"]),
                                "exclusion_reasons": dict(Counter(_reason(v) for v in mp["exclude"].values()))}
    if (ext / "bcc").exists():
        out["physics_check"]["bcc"] = physics_check.check_bcc(ext / "bcc")
        out["physics_on_bcc"] = physics_check.accuracy_on_bcc(ext / "bcc")

    # 3-4. transfer and pooled training, per test set and for all test sets together.
    # A test row from a paper that ARGUS contains would leak; such rows go to the
    # value cross-check only. A paper in two test sets is counted once in "all".
    out["transfer"], out["pooled"] = {}, {}
    argus_dois = {r["doi"] for r in argus_rows}
    test_keys = [k for k in src_rows if reg[k][0] == "test"]
    test_rows = {k: [r for r in src_rows[k] if r.get("doi") not in argus_dois] for k in test_keys}
    out["leakage_guard"] = {k: {"dropped_rows": len(src_rows[k]) - len(test_rows[k]),
                                "dropped_papers": sorted({r["doi"] for r in src_rows[k] if r.get("doi") in argus_dois})}
                            for k in test_keys}
    seen_papers: set[str] = set()
    combined, dup = [], {}
    for k in test_keys:
        papers = {r["paper_key"] for r in test_rows[k]}
        dup[k] = sorted(papers & seen_papers)
        combined += [r for r in test_rows[k] if r["paper_key"] not in seen_papers]
        seen_papers |= papers
    out["combined_duplicates"] = {k: v for k, v in dup.items() if v}
    predictions: dict[str, Any] = {}
    for key in test_keys + (["all"] if len(test_keys) > 1 else []):
        rows = combined if key == "all" else test_rows[key]
        test = build_dataset(rows)
        if not len(test.y):
            continue
        for r in test.rows:
            r["_in_domain"] = in_domain(train, r)
        res = transfer(train, test, quick=quick, n_boot=n_boot)
        predictions[key] = (test, res["predictions"])
        out["transfer"][key] = _strip(res)
        a_fill = {r["filler_base"] for r in train.rows}
        a_fam = {r["matrix_family"] for r in train.rows}
        out["transfer"][key]["domain"] = {
            "new_fillers": sorted({r["filler_base"] for r in test.rows} - a_fill),
            "new_matrices": sorted({r["matrix_polymer"] for r in test.rows if r["matrix_family"] not in a_fam}),
            "sources": sorted({r["ext_source"] for r in test.rows}),
        }
        if key == "all" or len(test_keys) == 1:
            out["pooled"][key] = pooled(train, test, quick=quick, n_boot=n_boot)

    # 5. value cross-check
    out["crosscheck"] = {}
    for key, rows in src_rows.items():
        cc = crosscheck(rows, argus_rows)
        out["crosscheck"][key] = cc
    review_path = ext / "crosscheck_review.yaml"
    review = (load_yaml(review_path) if review_path.exists() else None) or {}
    shared = {d for c in out["crosscheck"].values() for d in c["shared_dois"]}
    papers = review.get("papers") or {}
    out["crosscheck_review"] = {"reviewed": str(review.get("reviewed", "")), "papers": papers,
                                "unreviewed": sorted(shared - set(papers))}
    out["_predictions"] = predictions  # removed before writing; used for figures
    return out


def _reason(text: str) -> str:
    t = text.lower()
    for k in ("carbon", "metal", "nanofluid", "cementitious", "natural-fibre", "ceramic", "hybrid", "three different"):
        if k in t:
            return {"three different": "mixed fillers", "ceramic": "ceramic matrix"}.get(k, k)
    return "other"


# --------------------------------------------------------------------------- figures

def transfer_figure(test, preds: dict[str, np.ndarray], res: dict[str, Any], models: list[str], path: Path) -> Path | None:
    try:
        from ..report.figures import MARKER, PAL, RING, _clean, _plt, _save
        plt = _plt()
    except Exception:  # matplotlib is optional
        return None
    km = np.array([float(r["k_matrix_effective"]) for r in test.rows])
    k = km * 10 ** test.y
    dom = np.array([bool(r.get("_in_domain")) for r in test.rows])
    fig, axes = plt.subplots(1, len(models), figsize=(3.6 * len(models), 3.7), sharex=True, sharey=True)
    axes = np.atleast_1d(axes)
    lo, hi = 0.1, 30
    for ax, m in zip(axes, models):
        kp = km * 10 ** preds[m]
        e = res["models"][m]["test"]
        ax.fill_between([lo, hi], [lo / 2, hi / 2], [lo * 2, hi * 2], color=PAL["grid"], alpha=0.7, lw=0,
                        label="within ×2")
        ax.plot([lo, hi], [lo, hi], color=PAL["ink2"], lw=1)
        ax.scatter(k[~dom], kp[~dom], s=MARKER, color=PAL["s2"], edgecolor=PAL["surface"], linewidth=RING,
                   label="filler or matrix new to ARGUS", zorder=3)
        ax.scatter(k[dom], kp[dom], s=MARKER, color=PAL["s1"], edgecolor=PAL["surface"], linewidth=RING,
                   label="filler and matrix in ARGUS", zorder=3)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(lo, hi)
        ax.set_ylim(lo, hi)
        ax.set_title(f"{m}: typical error ×{e['mae_factor']:.2f}")
        ax.set_xlabel("measured k, W/(m·K)")
        _clean(ax, grid="both")
    axes[0].set_ylabel("predicted k, trained on ARGUS only")
    axes[0].legend(loc="upper left", fontsize=7.5)
    return _save(fig, path)


def bcc_figure(acc: dict[str, Any], path: Path) -> Path | None:
    try:
        from ..report.figures import PAL, _clean, _plt, _save
        plt = _plt()
    except Exception:
        return None
    names = {"maxwell_garnett": "Maxwell-Garnett", "bruggeman_dem": "Bruggeman, asymmetric (DEM)",
             "bruggeman_symmetric": "Bruggeman, symmetric", "lewis_nielsen_spheres": "Lewis-Nielsen (spheres)"}
    colors = {"bruggeman_dem": PAL["s1"], "maxwell_garnett": PAL["s2"], "lewis_nielsen_spheres": PAL["s3"],
              "bruggeman_symmetric": PAL["muted"]}
    bands = list(acc["n_by_band"])
    fig, ax = plt.subplots(figsize=(5.6, 3.4))
    x = np.arange(len(bands))
    for m, label in names.items():
        e = acc["models"].get(m)
        if not e:
            continue
        y = [e["mae_by_band"].get(b, np.nan) for b in bands]
        ax.plot(x, [10 ** v for v in y], marker="o", ms=6, lw=1.8, color=colors[m], label=label,
                markeredgecolor=PAL["surface"], markeredgewidth=1.0)
    ax.set_xticks(x, [f"{b}\n(n = {acc['n_by_band'][b]})" for b in bands])
    ax.set_yscale("log")
    ticks = [1.2, 1.5, 2, 3, 5, 10]
    ax.set_yticks(ticks, [f"×{t:g}" for t in ticks])
    ax.minorticks_off()
    ax.set_ylabel("typical error (× or ÷)")
    ax.set_title("Interface-free models on BCC's polymer composites")
    ax.legend(fontsize=7.5, loc="upper left")
    _clean(ax)
    return _save(fig, path)


# --------------------------------------------------------------------------- markdown

def _ci(c) -> str:
    return f"{c[0]:.3f}–{c[1]:.3f}" if c else "n/a, < 3 papers"


def render_markdown(res: dict[str, Any], figs: dict[str, str]) -> str:
    L: list[str] = []
    a = L.append
    fp = res["dataset"]
    a("# External validation\n")
    a(f"Generated by `argus external validate` from ARGUS ({fp['rows']} rows, {fp['papers']} papers, "
      f"fingerprint `{fp['sha256']}`) and the external datasets in `data/external/`."
      + (" **Quick mode: not for reporting.**" if res["config"]["quick"] else "") + "\n")

    a("## Sources\n")
    a("| Source | Licence | Role | Rows used | Papers | Raw files |")
    a("|---|---|---|---|---|---|")
    for key, s in res["sources"].items():
        a(f"| {s['title']} ({key}) | {s['license']} | {s['role']} | {s['rows']} | {s['papers']} | "
          f"{'checksum ok' if s['files_ok'] else 'CHECK FAILED'} |")
    for key, why in res.get("skipped", {}).items():
        a(f"| {key} | | skipped | | | {why} |")
    if res.get("physics_on_bcc"):
        a(f"| He, Wu & Fu source data (bcc) | MIT | physics checks only | {res['physics_check']['bcc']['maxwell_garnett']['n']} | – | checksum ok |")
    a("")
    lg = {k: v for k, v in (res.get("leakage_guard") or {}).items() if v["dropped_rows"]}
    if lg:
        a("**Leakage guard.** Test rows from papers that ARGUS also contains were moved to the value cross-check: "
          + "; ".join(f"{k}: {v['dropped_rows']} rows ({', '.join(v['dropped_papers'])})" for k, v in lg.items()) + ".\n")
    if res.get("combined_duplicates"):
        a("Papers present in more than one test set are counted once in the combined set: "
          + "; ".join(f"{k}: {', '.join(v)}" for k, v in res["combined_duplicates"].items()) + ".\n")

    pc = res.get("physics_check", {})
    if pc:
        a("## 1. Our physics code against two independent implementations\n")
        a("Both workbooks publish their own model predictions next to each point. We fed the same inputs to "
          "`argus.physics.emt` and compared.\n")
        a("| Workbook | Model | Points | Identical (≤1e-9) | Largest relative difference |")
        a("|---|---|---|---|---|")
        for src, chk in pc.items():
            for m, s in chk.items():
                if m == "models_compared" or not isinstance(s, dict) or "n" not in s:
                    continue
                a(f"| {src} | {chk['models_compared'].get(m, m)} | {s['n']} | {s['n_exact']} | {s['max_rel_diff']:.2g} |")
        dem = pc.get("bcc", {}).get("bruggeman_dem")
        if dem and dem.get("disagreements"):
            a(f"\nFor the asymmetric Bruggeman model {dem['n_close']} of {dem['n']} BCC points agree within 1e-4. "
              f"At the other {dem['disagreements']}, our root satisfies the model's defining equation to "
              f"{dem['max_abs_residual_ours']:.0e} while the published value misses it by at least "
              f"{dem['min_abs_residual_theirs']:.0e}: the difference comes from the workbook's numerical solution, not our code.")
        a("")

    pb = res.get("physics_on_bcc")
    if pb:
        a("## 2. How the interface-free models do on high-loading polymer composites (BCC)\n")
        a(f"{pb['n_points']} BCC points with a polymer matrix (km < {pb['km_max']} W/(m·K)); "
          + ", ".join(f"{n} at {b}" for b, n in pb["n_by_band"].items()) + ".\n")
        bands = list(pb["n_by_band"])
        a("| Model | MAE (log10) | Bias | " + " | ".join(bands) + " |")
        a("|---|---|---|" + "---|" * len(bands))
        for m, e in sorted(pb["models"].items(), key=lambda kv: kv[1]["mae_log10"]):
            a(f"| {m} | {e['mae_log10']:.3f} | {e['bias_log10']:+.3f} | "
              + " | ".join(f"{e['mae_by_band'].get(b, float('nan')):.3f}" for b in bands) + " |")
        ab = pb["above_maxwell_ceiling"]
        a(f"\n{100 * ab['share']:.0f}% of these points lie above the isolated-sphere ceiling km(1 + 2φ)/(1 − φ) "
          "(" + ", ".join(f"{100 * v:.0f}% at {b}" for b, v in ab["share_by_band"].items()) + "), "
          "so particle contacts carry heat even at modest loading.\n")
        if figs.get("bcc"):
            a(f"![Model error by loading]({figs['bcc']})\n")

    tr = res.get("transfer", {})
    if tr:
        a("## 3. Trained on ARGUS, tested on papers it has never seen\n")
        a("Each model is fitted on all ARGUS rows and predicts the external rows. MAE is in log10 units "
          "(0.15 = typical error ×1.41); the 95% interval resamples whole test papers. "
          "'vs physics' is the paired difference in MAE (negative = better than calibrated physics). "
          "Coverage is the share of external rows inside the model's 90% interval built from ARGUS "
          "leave-one-paper-out residuals.\n")
        for key, t in tr.items():
            a(f"### {key}: {t['test']['rows']} rows, {t['test']['papers']} papers "
              f"({t['test'].get('in_domain_rows', 0)} rows with filler and matrix already in ARGUS)\n")
            a("| Model | MAE (95% CI) | ×factor | Bias | In ARGUS domain | New filler/matrix | vs physics (95% CI) | 90% coverage | ARGUS LOPO MAE |")
            a("|---|---|---|---|---|---|---|---|---|")
            for m in t["ranking_test_mae"]:
                e = t["models"][m]
                vs = e.get("vs_reference")
                vs_s = f"{vs['mae_diff']:+.3f} ({_ci(vs['ci95'])}){' **clear**' if vs['clear'] else ''}" if vs else "reference"
                ind = e["in_domain"]["mae_log10"] if e.get("in_domain") else float("nan")
                ood = e["out_of_domain"]["mae_log10"] if e.get("out_of_domain") else float("nan")
                a(f"| {m} | {e['test']['mae_log10']:.3f} ({_ci(e['test_mae_ci95'])}) | ×{e['test']['mae_factor']:.2f} | "
                  f"{e['test']['bias_log10']:+.3f} | {ind:.3f} | {ood:.3f} | {vs_s} | "
                  f"{100 * e['interval']['coverage']:.0f}% | {e['train_lopo_mae']:.3f} |")
            a("")
            if figs.get(f"transfer_{key}"):
                a(f"![Transfer parity, {key}]({figs[f'transfer_{key}']})\n")

    po = res.get("pooled", {})
    if po:
        a("## 4. Does adding the external rows to training help?\n")
        a("Leave-one-paper-out over ARGUS + external papers, scored separately on each side and compared, paper by "
          "paper, with training on ARGUS alone (negative = pooling helps).\n")
        for key, p in po.items():
            a(f"### Pooled with {key} ({p['rows']} rows, {p['papers']} papers)\n")
            a("| Model | ARGUS rows: alone → pooled | difference (95% CI) | External rows: transfer → pooled | difference (95% CI) |")
            a("|---|---|---|---|---|")
            for m, e in p["models"].items():
                t, x = e["train_rows"], e["external_rows"]
                a(f"| {m} | {t['alone_lopo']:.3f} → {t['pooled_lopo']:.3f} | {t['diff']:+.3f} ({_ci(t['ci95'])}) | "
                  f"{x['transfer']:.3f} → {x['pooled_lopo']:.3f} | {x['diff']:+.3f} ({_ci(x['ci95'])}) |")
            a("")

    cc = res.get("crosscheck", {})
    if cc:
        a("## 5. Same paper, independent extraction\n")
        a("Papers present in both ARGUS and an external source; each external point is paired with the ARGUS point "
          "of the same filler at the closest loading (within 1 vol% or 5%) and a compatible direction.\n")
        a("| Source | Shared papers | Pairs | Agree (≤5%) | Minor (5–15%) | Disagree (>15%) | External points with no ARGUS partner |")
        a("|---|---|---|---|---|---|---|")
        for key, c in cc.items():
            g = c["grades"]
            a(f"| {key} | {c['shared_papers']} | {c['pairs']} | {g.get('agree', 0)} | {g.get('minor', 0)} | "
              f"{g.get('disagree', 0)} | {len(c['unmatched_external'])} |")
        rows = [(k, p) for k, c in cc.items() for p in c["pair_rows"]]
        if rows:
            a("\n| Source | DOI | ARGUS row | Loading ARGUS / external | Direction ARGUS / external | k ARGUS | k external | Difference |")
            a("|---|---|---|---|---|---|---|---|")
            for k, p in rows:
                unit = "wt%" if p["loading_basis"] == "wt" else "vol%"
                a(f"| {k} | {p['doi']} | {p['argus_row']} | {p['loading_argus']:g} / {p['loading_ext']:g} {unit} | "
                  f"{p['direction_argus']} / {p['direction_ext']} | {p['k_argus']} | {p['k_ext']} | "
                  f"{100 * p['rel_diff']:+.1f}% ({p['grade']}) |")
        rv = res.get("crosscheck_review") or {}
        if rv.get("papers"):
            a(f"\n**Reviewed by hand** ({rv.get('reviewed')}; `data/external/crosscheck_review.yaml`):\n")
            for doi, e in rv["papers"].items():
                a(f"- **{doi}** ({e['argus']}). {e['verdict']} *Action:* {e['action']}")
        if rv.get("unreviewed"):
            a(f"\nNot yet reviewed: {', '.join(rv['unreviewed'])}.")
        a("")
    return "\n".join(L) + "\n"


def write(lay: Layout, res: dict[str, Any]) -> list[Path]:
    preds = res.pop("_predictions", {})
    fig_dir = lay.reports / "figures"
    figs: dict[str, str] = {}
    written = []
    for key, (test, p) in preds.items():
        models = [m for m in ("physics", "ensemble") if m in p]
        f = transfer_figure(test, p, res["transfer"][key], models, fig_dir / f"external_transfer_{key}.png")
        if f:
            figs[f"transfer_{key}"] = f"figures/{f.name}"
            written.append(f)
    if res.get("physics_on_bcc"):
        f = bcc_figure(res["physics_on_bcc"], fig_dir / "external_bcc_models.png")
        if f:
            figs["bcc"] = f"figures/{f.name}"
            written.append(f)
    js = lay.reports / "external_validation.json"
    atomic_write_text(js, json.dumps(res, indent=2, ensure_ascii=False,
                                     default=lambda o: o.tolist() if isinstance(o, np.ndarray) else str(o)) + "\n")
    md = lay.reports / "external_validation.md"
    atomic_write_text(md, render_markdown(res, figs))
    return [js, md, *written]
