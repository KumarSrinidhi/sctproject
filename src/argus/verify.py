"""End-state verification: invariants that must hold before a release.

Supersedes work/final_verify.py. Read-only: it never rewrites deliverables (the
legacy script silently regenerated CSVs on mismatch, hiding drift). Writes a
machine-readable report to reports/verification.json.
"""
from __future__ import annotations

import datetime as _dt
import json
import re
import statistics
from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

from .build import expected_outputs, load_side_files, tombstone_ids
from .io import atomic_write_text
from .paths import Layout
from .records import compile_rows, load_records
from .validate import errors, summarize, validate_records

RECOVERED = re.compile(r"^(abstract-)?recovered\b", re.IGNORECASE)


@dataclass
class Check:
    id: str
    description: str
    ok: bool
    detail: str


@dataclass
class Report:
    generated: str
    overall: str = "PASS"
    checks: list[Check] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    def add(self, cid: str, desc: str, ok: bool, detail: str) -> bool:
        self.checks.append(Check(cid, desc, ok, detail))
        if not ok:
            self.overall = "FAIL"
        return ok

    def as_dict(self) -> dict[str, Any]:
        return {"generated": self.generated, "overall": self.overall,
                "checks": [asdict(c) for c in self.checks], "stats": self.stats}


def dataset_stats(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {"rows": 0}
    k = [float(r["k_composite_W_mK"]) for r in rows]
    years = [int(r["year"]) for r in rows if r["year"] != ""]
    return {
        "rows": len(rows),
        "papers": len({r["doi"] for r in rows}),
        "k_min": min(k), "k_max": max(k), "k_median": statistics.median(k),
        "year_min": min(years) if years else None, "year_max": max(years) if years else None,
        "confidence": dict(Counter(r["confidence"] for r in rows).most_common()),
        "value_source": dict(Counter(r["value_source"] for r in rows).most_common()),
        "filler_material": dict(Counter(r["filler_material"] for r in rows).most_common()),
    }


def verify(lay: Layout, write: bool = True) -> Report:
    rep = Report(generated=_dt.datetime.now().isoformat(timespec="seconds"))
    res = load_records(lay)
    rep.add("records_load", "All record files parse and match the schema", not res.errors,
            f"{len(res.records)} records; {len(res.errors)} schema errors"
            + (f" (first: {res.errors[0][0].name}: {res.errors[0][1]})" if res.errors else ""))

    issues = validate_records(res.records, tombstone_ids(lay))
    errs = errors(issues)
    rep.add("validation_clean", "No unwaived validation errors", not errs,
            f"{len(errs)} errors, {len(issues) - len(errs)} warnings: {summarize(issues)}")

    rows = compile_rows(res.records)
    outputs = expected_outputs(lay)
    drift = [p.name for p, data in outputs.items() if not p.exists() or p.read_bytes() != data]
    rep.add("outputs_in_sync",
            "Every generated file (CSVs, rows.jsonl, enriched table, datapackage.json) equals a fresh build",
            not drift, f"{len(outputs)} files in sync" if not drift else f"out of date: {drift} (run `argus build`)")

    curation, excl = load_side_files(lay)
    dataset_dois = {r["doi"] for r in rows}
    conflicts = [e["doi"] for e in excl if e["doi"] in dataset_dois and not RECOVERED.match(e.get("action", ""))]
    rep.add("exclusions_consistent", "A DOI with rows is never listed as excluded (unless marked recovered)",
            not conflicts, "consistent" if not conflicts else f"{len(conflicts)} conflicting: {conflicts}")

    no_log = [r.paper_id for r in res.records if not r.extraction_log]
    rep.add("papers_have_log", "Every paper has at least one extraction-log entry", not no_log,
            "all papers logged" if not no_log else f"missing for {no_log}")

    fig_bad = [r["row_id"] for r in rows if r["value_source"] == "figure"
               and not re.search(r"digiti[sz]", r["source_location"], re.IGNORECASE)]
    rep.add("figure_rows_cite_method", "Figure-derived rows name the digitization method", not fig_bad,
            f"{sum(r['value_source'] == 'figure' for r in rows)} figure rows" + (f"; missing: {fig_bad}" if fig_bad else ""))

    weak = [(r.paper_id, m.row_id) for r in res.records for m in r.measurements for w in m.waivers
            if len(w.reason.strip()) < 20]
    n_waivers = sum(len(m.waivers) for r in res.records for m in r.measurements)
    rep.add("waivers_justified", "Every waiver carries a written justification", not weak,
            f"{n_waivers} waivers" + (f"; unjustified: {weak}" if weak else ""))

    if lay.legacy_rows.exists():
        from .legacy import undeclared_legacy_diffs

        und = undeclared_legacy_diffs(lay)
        rep.add("changes_declared", "Every difference from the legacy v1.0 rows is declared in a curation-log entry",
                not und, "all declared" if not und else f"{len(und)} undeclared: {und[:5]}")

    rep.stats = dataset_stats(rows)
    if write:
        lay.reports.mkdir(exist_ok=True)
        atomic_write_text(lay.reports / "verification.json", json.dumps(rep.as_dict(), indent=2, ensure_ascii=False))
    return rep
