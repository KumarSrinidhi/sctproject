"""`argus` command line.

    argus validate          check every record against the rules
    argus build             compile records -> published CSVs (blocked by errors)
    argus verify            end-state invariants -> reports/verification.json
    argus stats             headline numbers
    argus new-paper         scaffold a record file for a new paper
    argus migrate-legacy    one-time import from work/ (already done)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer

from .paths import layout

app = typer.Typer(add_completion=False, no_args_is_help=True, help="ARGUS thermal conductivity dataset toolkit.")

RootOpt = typer.Option(None, "--root", help="Project root (default: auto-detect from cwd).")


def _utf8_stdout() -> None:
    # Windows consoles default to cp1252; record text contains μ, ·, −.
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
        except Exception:
            pass


_utf8_stdout()


@app.command()
def validate(root: Optional[Path] = RootOpt, show_warnings: bool = typer.Option(True, "--warnings/--no-warnings")):
    """Check every record against the validation rules."""
    from .build import tombstone_ids
    from .records import load_records
    from .validate import errors, summarize, validate_records

    lay = layout(root)
    res = load_records(lay)
    for p, e in res.errors:
        typer.echo(f"SCHEMA  {p.name}: {e}")
    issues = validate_records(res.records, tombstone_ids(lay))
    for i in issues:
        if i.severity == "error" or show_warnings:
            typer.echo(f"{i.severity.upper():7s} {i.paper_id} {i.row_id or '-':14s} {i.rule}: {i.message}")
    n_err = len(errors(issues)) + len(res.errors)
    n_meas = sum(len(r.measurements) for r in res.records)
    typer.echo(f"\n{len(res.records)} papers, {n_meas} measurements: {n_err} errors, "
               f"{len(issues) - len(errors(issues))} warnings  {summarize(issues) or ''}")
    raise typer.Exit(1 if n_err else 0)


@app.command()
def build(root: Optional[Path] = RootOpt, dry_run: bool = typer.Option(False, "--dry-run")):
    """Compile records into the published deliverables."""
    from .build import BuildBlocked, build as _build

    lay = layout(root)
    try:
        r = _build(lay, dry_run=dry_run)
    except BuildBlocked as e:
        for i in e.issues[:50]:
            typer.echo(f"ERROR   {i.paper_id} {i.row_id or '-':14s} {i.rule}: {i.message}")
        typer.echo(f"\nBuild blocked: {e}")
        raise typer.Exit(1)
    typer.echo(f"{r.rows} rows / {r.papers} papers / {r.uncertain} uncertain / "
               f"{r.log_entries} log entries / {r.exclusions} exclusions; {len(r.warnings)} warnings")
    if dry_run:
        typer.echo("dry run: nothing written")
    else:
        typer.echo("written: " + (", ".join(p.name for p in r.written) or "nothing changed"))


@app.command()
def verify(root: Optional[Path] = RootOpt):
    """Check release invariants and write reports/verification.json."""
    from .verify import verify as _verify

    rep = _verify(layout(root))
    for c in rep.checks:
        typer.echo(f"[{'PASS' if c.ok else 'FAIL'}] {c.id}: {c.detail}")
    typer.echo(f"\nOVERALL: {rep.overall}")
    raise typer.Exit(0 if rep.overall == "PASS" else 1)


@app.command()
def stats(root: Optional[Path] = RootOpt):
    """Print headline dataset numbers."""
    from .records import compile_rows, load_records
    from .verify import dataset_stats

    rows = compile_rows(load_records(layout(root)).records)
    typer.echo(json.dumps(dataset_stats(rows), indent=2, ensure_ascii=False))


@app.command()
def physics(root: Optional[Path] = RootOpt, min_points: int = typer.Option(3, help="Minimum distinct loadings per series")):
    """Fit effective-medium models to every loading series; write reports/physics_*."""
    from .enrich import enrich_records
    from .io import atomic_write_bytes, atomic_write_text, csv_bytes
    from .physics.fit import build_series, fit_series, fits_table, summarize
    from .records import load_records

    from .fingerprint import dataset_fingerprint

    lay = layout(root)
    records = load_records(lay).records
    rows = enrich_records(records)
    fits = [fit_series(s) for s in build_series(rows, min_points=min_points)]
    table = fits_table(fits)
    summary = summarize(fits, rows)
    summary["dataset"] = dataset_fingerprint(records)
    lay.reports.mkdir(exist_ok=True)
    if table:
        atomic_write_bytes(lay.reports / "physics_fits.csv", csv_bytes(table, list(table[0])))
    atomic_write_text(lay.reports / "physics_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    typer.echo(json.dumps(summary, indent=2, ensure_ascii=False))
    typer.echo(f"\nwrote reports/physics_fits.csv ({len(table)} series) and reports/physics_summary.json")


analyze_app = typer.Typer(no_args_is_help=True, help="Dataset-level analyses (read-only).")
app.add_typer(analyze_app, name="analyze")


@analyze_app.command("bias")
def analyze_bias(root: Optional[Path] = RootOpt):
    """Measurement-technique and direction bias -> reports/method_bias.{md,json}."""
    from .analysis.bias import analyze, render_markdown, uncertainty_rows
    from .enrich import enrich_records
    from .io import atomic_write_bytes, atomic_write_text, csv_bytes
    from .records import load_records

    from .fingerprint import dataset_fingerprint

    lay = layout(root)
    records = load_records(lay).records
    rows = enrich_records(records)
    res = analyze(rows)
    res["dataset"] = dataset_fingerprint(records)
    lay.reports.mkdir(exist_ok=True)
    atomic_write_text(lay.reports / "method_bias.json", json.dumps(res, indent=2, ensure_ascii=False) + "\n")
    atomic_write_text(lay.reports / "method_bias.md", render_markdown(res))
    u = uncertainty_rows(rows)
    atomic_write_bytes(lay.reports / "uncertainty_budget.csv", csv_bytes(u, list(u[0])))
    an, main = res["anisotropy"], res["pooled_models"]["main"]
    typer.echo(f"same-sample direction pairs: {an.get('n_pairs', 0)} (median k_in/k_through {an.get('A_median')}); "
               f"same-sample method pairs: {len(res['method_pairs'])}")
    if "effects" in main and "method:MIXED" in main["effects"]:
        e = main["effects"]["method:MIXED"]
        typer.echo(f"isotropic-mode sensors vs laser flash (between papers): x{e['factor']} "
                   f"(95% CI {e['ci95'][0]}-{e['ci95'][1]}), {main['n']} rows / {main['papers']} papers")
    typer.echo("wrote reports/method_bias.md, reports/method_bias.json, reports/uncertainty_budget.csv")


ml_app = typer.Typer(no_args_is_help=True, help="Machine learning validated by holding out whole papers.")
app.add_typer(ml_app, name="ml")


@ml_app.command("benchmark")
def ml_benchmark(root: Optional[Path] = RootOpt,
                 quick: bool = typer.Option(False, "--quick", help="Fewer trees and repeats (for smoke tests)"),
                 ablate: bool = typer.Option(True, "--ablate/--no-ablate", help="Feature-group ablation for the best model")):
    """Baselines vs learned models under leave-one-paper-out CV -> reports/ml_benchmark.{md,json}."""
    import numpy as np

    from .enrich import enrich_records
    from .io import atomic_write_bytes, atomic_write_text, csv_bytes
    from .ml.benchmark import Config, ablation, run_benchmark
    from .ml.features import build_dataset
    from .ml.report import parity_plot, predictions_table, render_markdown
    from .records import load_records

    from .fingerprint import dataset_fingerprint

    lay = layout(root)
    records = load_records(lay).records
    ds = build_dataset(enrich_records(records))
    cfg = Config.fast() if quick else Config()
    typer.echo(f"{len(ds.y)} rows / {ds.n_papers} papers / {len(ds.names)} features; fitting models...")
    res = run_benchmark(ds, cfg)
    best = res["best_model"]
    abl = ablation(ds, best if best not in ("gp_residual", "ensemble") else "xgboost", cfg) if ablate and best else None
    lay.reports.mkdir(exist_ok=True)
    fig = parity_plot(ds, res, [m for m in ("physics", "knn", best) if m in res["models"]],
                      lay.reports / "figures" / "ml_parity_lopo.png")
    table = predictions_table(ds, res, best)
    atomic_write_bytes(lay.reports / "ml_lopo_predictions.csv", csv_bytes(table, list(table[0])))
    serial = {k: v for k, v in res.items() if k != "lopo_predictions"}
    serial["ablation"] = abl
    serial["dataset"] = dataset_fingerprint(records)
    serial["config"] = {"quick": cfg.quick, "repeats": cfg.repeats, "ablation_repeats": cfg.ablation_repeats}
    atomic_write_text(lay.reports / "ml_benchmark.json", json.dumps(serial, indent=2, ensure_ascii=False,
                                                                    default=lambda o: o.tolist() if isinstance(o, np.ndarray) else str(o)) + "\n")
    atomic_write_text(lay.reports / "ml_benchmark.md",
                      render_markdown(res, abl, "figures/ml_parity_lopo.png" if fig else None))
    for n in res["ranking_lopo_mae"]:
        e = res["models"][n]["lopo"]
        typer.echo(f"  {n:14s} LOPO MAE {e['mae_log10']:.3f} (x{e['mae_factor']:.2f})  R2 {e['r2']:.2f}  "
                   f"within x2 {100 * e['within_factor_2']:.0f}%")
    acc = res.get("acceptance", {})
    typer.echo(f"acceptance: {'PASS' if acc.get('passed') else 'FAIL'} ({best} vs {res['best_baseline']})")
    typer.echo("wrote reports/ml_benchmark.md, ml_benchmark.json, ml_lopo_predictions.csv"
               + (", figures/ml_parity_lopo.png" if fig else ""))


acquire_app = typer.Typer(no_args_is_help=True, help="Phase 6: discover, screen and fetch new open-access papers.")
app.add_typer(acquire_app, name="acquire")


@acquire_app.command("search")
def acquire_search(root: Optional[Path] = RootOpt,
                   max_per_query: Optional[int] = typer.Option(None, help="Override max_results_per_query")):
    """Run data/acquisition/queries.yaml on OpenAlex, screen, write candidates.csv (queries logged)."""
    from collections import Counter

    from .acquire.keys import MissingKey
    from .acquire.run import search

    lay = layout(root)
    try:
        rows = search(lay, max_per_query)
    except MissingKey as e:
        typer.echo(str(e))
        raise typer.Exit(2)
    c = Counter(r["reason_code"] for r in rows)
    typer.echo(f"{len(rows)} distinct DOIs; " + ", ".join(f"{k} {v}" for k, v in c.most_common()))
    typer.echo("wrote data/acquisition/candidates.csv; queries appended to data/acquisition/queries.jsonl")


@acquire_app.command("fetch")
def acquire_fetch(root: Optional[Path] = RootOpt, limit: int = typer.Option(20, help="How many papers to fetch")):
    """Europe PMC JATS full text for included candidates with a PMCID (cached in sources/, git-ignored)."""
    from .acquire.run import fetch

    lay = layout(root)
    done = fetch(lay, limit)
    for r in done:
        typer.echo(f"{r['doi']:40s} {r['jats_licence'][:50]:50s} {r['jats']}")
    typer.echo(f"{len(done)} full texts fetched")


@acquire_app.command("import")
def acquire_import(extraction: Path = typer.Argument(..., help="data/acquisition/extractions/<batch>.json"),
                   root: Optional[Path] = RootOpt, dry_run: bool = typer.Option(False, "--dry-run")):
    """Create records from checked extractions (verifier verdicts applied; quotes re-checked)."""
    from .acquire.importer import import_batch
    from .acquire.run import cache_dir, read

    lay = layout(root)
    data = json.loads((extraction if extraction.is_absolute() else lay.root / extraction).read_text(encoding="utf-8"))
    meta = {r["doi"]: {"title": r["title"], "year": r["year"], "license": r["license"]} for r in read(lay)}
    rep = import_batch(lay, data["papers"], data["verdicts"], meta, cache_dir(lay) / "text", dry_run=dry_run)
    typer.echo(f"{'would create' if dry_run else 'created'} {len(rep.created)} records ({', '.join(rep.created)}), "
               f"{rep.rows_added} rows; {len(rep.excluded)} papers excluded; {len(rep.rejected)} candidate rows rejected")
    for doi, why in rep.excluded:
        typer.echo(f"  excluded {doi}: {why[:120]}")
    for doi, i, why in rep.rejected:
        typer.echo(f"  rejected {doi} row {i}: {why[:120]}")


release_app = typer.Typer(no_args_is_help=True, help="Release artefacts (Zenodo upload bundle).")
app.add_typer(release_app, name="release")


def _data_differs_from_tag(lay, tag: str) -> str | None:
    """The tag name if git has `tag` and its published table differs from the working copy, else None."""
    import subprocess

    try:
        r = subprocess.run(["git", "show", f"{tag}:thermal_conductivity_dataset.csv"], cwd=lay.root,
                           capture_output=True, stdin=subprocess.DEVNULL)
    except OSError:
        return None
    if r.returncode != 0:  # no such tag (an unreleased version) or not a git checkout
        return None
    norm = lambda b: b.replace(b"\r\n", b"\n")  # noqa: E731  (checkout line endings may differ)
    return tag if norm(r.stdout) != norm(lay.dataset_csv.read_bytes()) else None


@release_app.command("bundle")
def release_bundle(root: Optional[Path] = RootOpt,
                   out: Path = typer.Option(Path("dist"), "--out", help="Output folder (relative to the project root)")):
    """Zip the dataset files (no code, no third-party papers) for a Zenodo upload -> dist/."""
    from .build import expected_outputs
    from .release import build_bundle, dataset_meta

    lay = layout(root)
    stale = [p.name for p, data in expected_outputs(lay).items() if not p.exists() or p.read_bytes() != data]
    if stale:
        typer.echo(f"Published files are out of date ({stale}); run `argus build` first.")
        raise typer.Exit(1)
    meta = dataset_meta(lay)
    changed = _data_differs_from_tag(lay, f"data-v{'.'.join(str(meta.get('version', '')).split('.')[:2])}")
    if changed:
        typer.echo(f"The dataset differs from the released tag {changed} but data/dataset.yaml still says version "
                   f"{meta.get('version')}. Bump the version (and CHANGELOG) before bundling, or bundle from that tag.")
        raise typer.Exit(1)
    out_dir = out if out.is_absolute() else lay.root / out
    path, digest = build_bundle(lay, out_dir)
    import zipfile

    with zipfile.ZipFile(path) as z:
        n_files = len(z.namelist())
    typer.echo(f"wrote {path} ({path.stat().st_size // 1024} KB, {n_files} files)")
    typer.echo(f"sha256 {digest}")
    typer.echo(f"Zenodo metadata: .zenodo.json (version {meta.get('version')}, licence {meta.get('license')})")


report_app = typer.Typer(no_args_is_help=True, help="Course report generated from the analysis outputs.")
app.add_typer(report_app, name="report")


@report_app.command("course")
def report_course(root: Optional[Path] = RootOpt):
    """Render docs/course_report/COURSE_REPORT.md and its figures from current results."""
    from .fingerprint import StaleAnalysis
    from .report.course import render

    lay = layout(root)
    try:
        out = render(lay)
    except StaleAnalysis as e:
        typer.echo(f"Cannot render: {e}")
        raise typer.Exit(1)
    typer.echo(f"wrote {out.relative_to(lay.root)} and {len(list((out.parent / 'figures').glob('*.png')))} figures")


@report_app.command("explorer")
def report_explorer(root: Optional[Path] = RootOpt):
    """Render the interactive explorer: docs/explorer/index.html (+ an artifact fragment)."""
    from .fingerprint import StaleAnalysis
    from .report.explorer import render

    lay = layout(root)
    try:
        paths = render(lay)
    except StaleAnalysis as e:
        typer.echo(f"Cannot render: {e}")
        raise typer.Exit(1)
    for name, p in paths.items():
        typer.echo(f"wrote {p.relative_to(lay.root)} ({p.stat().st_size // 1024} KB, {name})")


external_app = typer.Typer(no_args_is_help=True, help="External datasets: fetch, check, and test ARGUS against them.")
app.add_typer(external_app, name="external")


@external_app.command("fetch")
def external_fetch(source: Optional[str] = typer.Argument(None, help="Source key (default: all)"),
                   root: Optional[Path] = RootOpt):
    """Download missing raw files listed in data/external/sources.yaml (sha256-checked)."""
    from .external.manifest import UnknownSource, fetch

    lay = layout(root)
    try:
        results = fetch(lay.data / "external", only=source)
    except UnknownSource as e:
        typer.echo(str(e.args[0]))
        raise typer.Exit(2)
    bad = 0
    for r in results:
        bad += r["action"] in ("checksum-mismatch", "download-failed")
        typer.echo(f"{r['action']:18s} {r['source']:8s} {r['path']}" + (f"  ({r['error']})" if r.get("error") else ""))
    raise typer.Exit(1 if bad else 0)


@external_app.command("check")
def external_check(root: Optional[Path] = RootOpt):
    """Verify every external raw file against its recorded sha256."""
    from .external.manifest import check_files

    lay = layout(root)
    files = check_files(lay.data / "external")
    for f in files:
        state = "ok" if f["ok"] else ("MISSING" if not f["present"] else "CHANGED")
        if not f["present"] and not f["committed"]:
            state = "not fetched (run `argus external fetch`)"
        typer.echo(f"{state:12s} {f['source']:8s} {f['path']}")
    raise typer.Exit(0 if all(f["ok"] or (not f["present"] and not f["committed"]) for f in files) else 1)


@external_app.command("validate")
def external_validate(root: Optional[Path] = RootOpt,
                      quick: bool = typer.Option(False, "--quick", help="Fewer trees and bootstrap draws (smoke tests)")):
    """Physics cross-check, transfer, pooled training and value cross-check -> reports/external_validation.{md,json}."""
    import warnings

    from .external.report import run, write

    warnings.filterwarnings("ignore", category=UserWarning)
    lay = layout(root)
    res = run(lay, quick=quick, n_boot=200 if quick else 2000)
    for key, why in res.get("skipped", {}).items():
        typer.echo(f"skipped {key}: {why}")
    for key, t in res["transfer"].items():
        best = t["ranking_test_mae"][0]
        e = t["models"][best]
        typer.echo(f"transfer to {key}: {t['test']['rows']} rows / {t['test']['papers']} papers; best {best} "
                   f"MAE {e['test']['mae_log10']:.3f} (x{e['test']['mae_factor']:.2f}); physics "
                   f"{t['models']['physics']['test']['mae_log10']:.3f}")
    for key, c in res["crosscheck"].items():
        if c["shared_papers"]:
            typer.echo(f"cross-check {key}: {c['shared_papers']} shared papers, {c['pairs']} pairs {c['grades']}")
    paths = write(lay, res)
    typer.echo("wrote " + ", ".join(str(p.relative_to(lay.root)) for p in paths))


@app.command("new-paper")
def new_paper(
    doi: str = typer.Option(..., help="DOI, e.g. 10.3390/polym12345678"),
    title: str = typer.Option(..., help="Paper title (check against Crossref)"),
    year: int = typer.Option(..., help="Publication year"),
    root: Optional[Path] = RootOpt,
):
    """Create a record skeleton for a new paper with the next free paper id."""
    from .records import load_records, next_paper_id, record_filename, save_record
    from .schema import PaperMeta, PaperRecord

    lay = layout(root)
    res = load_records(lay)
    doi = doi.strip().lower().removeprefix("https://doi.org/")
    if any(r.paper.doi.lower() == doi for r in res.records):
        typer.echo(f"{doi} already has a record")
        raise typer.Exit(1)
    pid = next_paper_id(res.records)
    rec = PaperRecord(paper_id=pid, paper=PaperMeta(doi=doi, title=title, year=year,
                                                    source_url=f"https://doi.org/{doi}"))
    path = save_record(lay, rec)
    typer.echo(f"created {path.relative_to(lay.root)} ({record_filename(pid, doi)})")


@app.command("migrate-legacy")
def migrate_legacy(root: Optional[Path] = RootOpt, overwrite: bool = typer.Option(False, "--overwrite")):
    """Import work/rows_raw.jsonl + logs into data/records (lossless, verified)."""
    from .legacy import migrate, verify_migration

    lay = layout(root)
    s = migrate(lay, overwrite=overwrite)
    typer.echo(f"migrated: {s}")
    diffs = verify_migration(lay)
    typer.echo("round-trip: lossless" if not diffs else f"round-trip: {len(diffs)} differences")
    for d in diffs[:20]:
        typer.echo("  " + d)
    raise typer.Exit(1 if diffs else 0)


def main() -> None:  # pragma: no cover
    app()


if __name__ == "__main__":  # pragma: no cover
    main()
