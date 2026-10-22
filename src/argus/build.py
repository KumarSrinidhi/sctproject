"""Compile curated records into the published deliverables.

Outputs are pure functions of data/: running `argus build` twice gives identical
bytes. The build refuses to write anything while unwaived validation errors exist.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .io import atomic_write_bytes, csv_bytes, jsonl_text, load_yaml
from .paths import Layout
from .records import compile_rows, load_records
from .schema import COLUMN_NAMES, PaperRecord
from .validate import Issue, errors, validate_records

INVENTORY_COLUMNS = ["doi", "paper_title", "year", "source_url", "rows_extracted",
                     "filler_materials", "matrix_polymers", "k_min_W_mK", "k_max_W_mK"]
LOG_COLUMNS = ["candidate_id", "doi", "paper_title", "date_processed", "access_result", "files_inspected",
               "tables_inspected", "figures_inspected", "candidate_measurements", "rows_appended",
               "unit_conversions", "duplicate_checks", "qc_findings", "rows_rejected_at_append"]
EXCLUSION_COLUMNS = ["doi", "reason", "action"]


class BuildBlocked(RuntimeError):
    def __init__(self, issues: list[Issue]):
        self.issues = issues
        super().__init__(f"{len(issues)} validation error(s); nothing was written")


@dataclass
class BuildResult:
    rows: int
    papers: int
    uncertain: int
    log_entries: int
    exclusions: int
    written: list[Path] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)
    enrichment_qa: dict[str, Any] = field(default_factory=dict)


def inventory(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    papers: dict[str, dict[str, Any]] = {}
    for r in rows:
        p = papers.setdefault(r["doi"], {
            "doi": r["doi"], "paper_title": r["paper_title"], "year": r["year"],
            "source_url": r["source_url"], "rows_extracted": 0,
            "fm": set(), "mp": set(), "k_min_W_mK": None, "k_max_W_mK": None,
        })
        p["rows_extracted"] += 1
        p["fm"].add(r["filler_material"])
        p["mp"].add(r["matrix_polymer"])
        k = float(r["k_composite_W_mK"])
        p["k_min_W_mK"] = k if p["k_min_W_mK"] is None else min(p["k_min_W_mK"], k)
        p["k_max_W_mK"] = k if p["k_max_W_mK"] is None else max(p["k_max_W_mK"], k)
    out = []
    for doi in sorted(papers):
        p = papers[doi]
        p["filler_materials"] = "; ".join(sorted(p.pop("fm")))
        p["matrix_polymers"] = "; ".join(sorted(p.pop("mp")))
        out.append(p)
    return out


def log_entries(records: list[PaperRecord], curation: list[dict[str, Any]]) -> list[dict[str, Any]]:
    entries = [e for rec in records for e in rec.extraction_log] + list(curation)
    entries.sort(key=lambda e: e.get("seq", 10**9))
    out = []
    for e in entries:
        row = {c: e.get(c, "") for c in LOG_COLUMNS}
        rej = e.get("rows_rejected_at_append")
        if rej:
            row["rows_rejected_at_append"] = "; ".join(f"{rid}:{reason}" for rid, reason in rej)
        out.append(row)
    return out


def _yaml_list(path: Path, key: str) -> list[dict[str, Any]]:
    return (load_yaml(path) or {}).get(key, []) if path.exists() else []


def load_side_files(lay: Layout) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return _yaml_list(lay.curation_log, "entries"), _yaml_list(lay.exclusions, "exclusions")


def tombstone_ids(lay: Layout) -> set[str]:
    return {t["row_id"] for t in _yaml_list(lay.tombstones, "tombstones")}


def render_outputs(lay: Layout, records: list[PaperRecord]) -> dict[Path, bytes]:
    """Every generated file and its exact bytes. Shared by build and verify."""
    from .enrich import expected_enriched_bytes
    from .package import descriptor_text
    from .release import citation_cff, dataset_meta

    rows = compile_rows(records)
    curation, excl = load_side_files(lay)
    inv = inventory(rows)
    meta = dataset_meta(lay)
    outputs = {
        lay.dataset_csv: csv_bytes(rows, COLUMN_NAMES),
        lay.uncertain_csv: csv_bytes([r for r in rows if r["confidence"] != "High"], COLUMN_NAMES),
        lay.inventory_csv: csv_bytes(inv, INVENTORY_COLUMNS),
        lay.log_csv: csv_bytes(log_entries(records, curation), LOG_COLUMNS),
        lay.unusable_csv: csv_bytes(excl, EXCLUSION_COLUMNS, bom=False),
        lay.compiled_jsonl: jsonl_text(rows).encode("utf-8"),
        lay.processed / "measurements_enriched.csv": expected_enriched_bytes(records),
        lay.root / "datapackage.json": descriptor_text(lay, {"rows": len(rows), "papers": len(inv)}).encode("utf-8"),
    }
    if meta.get("authors"):  # release metadata present: publish the citation file
        outputs[lay.root / "CITATION.cff"] = citation_cff(meta).encode("utf-8")
    return outputs


def build(lay: Layout, dry_run: bool = False) -> BuildResult:
    from .enrich import enrich_records, qa_summary

    res = load_records(lay)
    if res.errors:
        raise BuildBlocked([Issue("schema", "error", p.stem.split("_")[0], "", e) for p, e in res.errors])
    issues = validate_records(res.records, tombstone_ids(lay))
    blocking = errors(issues)
    if blocking:
        raise BuildBlocked(blocking)

    rows = compile_rows(res.records)
    curation, excl = load_side_files(lay)
    result = BuildResult(
        rows=len(rows), papers=len({r["doi"] for r in rows}),
        uncertain=sum(r["confidence"] != "High" for r in rows),
        log_entries=len(log_entries(res.records, curation)), exclusions=len(excl),
        warnings=[i for i in issues if i.severity == "warning"],
        enrichment_qa=qa_summary(enrich_records(res.records)),
    )
    if dry_run:
        return result
    for path, data in render_outputs(lay, res.records).items():
        if not path.exists() or path.read_bytes() != data:
            atomic_write_bytes(path, data)
            result.written.append(path)
    qa_path = lay.reports / "enrichment_qa.json"
    qa_bytes = (json.dumps(result.enrichment_qa, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if not qa_path.exists() or qa_path.read_bytes() != qa_bytes:
        atomic_write_bytes(qa_path, qa_bytes)
        result.written.append(qa_path)
    return result


def expected_outputs(lay: Layout) -> dict[Path, bytes]:
    """What `build` would write, without writing (used by verify for drift checks)."""
    return render_outputs(lay, load_records(lay).records)
