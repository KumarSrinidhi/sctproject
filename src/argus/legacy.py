"""One-time migration of the legacy pipeline (work/) into curated records (data/).

Lossless by construction and checked by `verify_migration`: compiling the new
records must reproduce work/rows_raw.jsonl field for field, and the rebuilt
deliverable CSVs must be byte-identical to the ones published at Phase 4.
"""
from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from .io import atomic_write_text, dump_yaml, read_csv, read_jsonl
from .paths import Layout
from .records import compile_rows, load_records, save_record
from .schema import (
    COLUMN_NAMES,
    Measurement,
    PaperMeta,
    PaperRecord,
    Waiver,
    row_to_measurement_fields,
)

# Reviewed exceptions that existed before migration (QC report section 2).
KNOWN_WAIVERS: dict[str, list[Waiver]] = {
    "bf4f3fd7-182": [Waiver(
        rule="loading_present",
        reason="Source gives only the BN/PA66 scaffold sample designation '30-4', not a wt% or "
               "vol%; documented exception since Phase 2 (quality_control_report.md section 2).",
    )],
}

CURATION_HEADER = (
    "# Pipeline-level log entries that are not about a single paper\n"
    "# (bulk remediation passes, multi-paper upgrades). `seq` is the position in\n"
    "# the chronological extraction log.\n"
)
EXCLUSIONS_HEADER = (
    "# Sources excluded at screening or extraction, with the reason. An action of\n"
    "# 'recovered' or 'abstract-recovered' means rows were later recovered after all.\n"
    "# Compiled to unusable_sources.csv. Add an entry whenever a candidate is dropped\n"
    "# so that every exclusion is auditable (audit finding D10).\n"
)


@dataclass
class MigrationSummary:
    papers: int
    measurements: int
    paper_log_entries: int
    curation_log_entries: int
    exclusions: int


def migrate(lay: Layout, overwrite: bool = False) -> MigrationSummary:
    if lay.records.exists() and any(lay.records.glob("*.yaml")) and not overwrite:
        raise FileExistsError(f"{lay.records} already has records; pass overwrite=True to redo")
    rows = read_jsonl(lay.legacy_rows)
    log = read_jsonl(lay.legacy_log)

    # Papers in order of first appearance (matches candidate ids P001..P093, then
    # the two Phase-4 figure papers).
    papers: "OrderedDict[str, list[dict[str, Any]]]" = OrderedDict()
    for r in rows:
        papers.setdefault(r["doi"], []).append(r)

    by_doi_log: dict[str, list[dict[str, Any]]] = {d: [] for d in papers}
    curation: list[dict[str, Any]] = []
    for seq, entry in enumerate(log, 1):
        e = {"seq": seq, **entry}
        if entry.get("doi") in by_doi_log:
            by_doi_log[entry["doi"]].append(e)
        else:
            curation.append(e)

    lay.records.mkdir(parents=True, exist_ok=True)
    if overwrite:
        for p in lay.records.glob("*.yaml"):
            p.unlink()
    n_meas = 0
    for i, (doi, prow) in enumerate(papers.items(), 1):
        first = prow[0]
        meta = PaperMeta(doi=doi, title=first["paper_title"], year=first["year"] or None,
                         source_url=first["source_url"] or None)
        ms = []
        for r in prow:
            m = Measurement(**row_to_measurement_fields(r))
            m.waivers = list(KNOWN_WAIVERS.get(m.row_id, []))
            ms.append(m)
        n_meas += len(ms)
        rec = PaperRecord(paper_id=f"P{i:03d}", paper=meta, extraction_log=by_doi_log[doi], measurements=ms)
        save_record(lay, rec)

    atomic_write_text(lay.curation_log, dump_yaml({"entries": curation}, header=CURATION_HEADER))

    excl = [dict(e) for e in read_csv(lay.unusable_csv)]
    atomic_write_text(lay.exclusions, dump_yaml({"exclusions": excl}, header=EXCLUSIONS_HEADER))

    atomic_write_text(lay.tombstones, dump_yaml({"tombstones": _phase2_tombstones(lay)},
                                                header=TOMBSTONES_HEADER))

    return MigrationSummary(len(papers), n_meas, sum(len(v) for v in by_doi_log.values()),
                            len(curation), len(excl))


TOMBSTONES_HEADER = (
    "# Row ids that were deliberately removed. They must never reappear\n"
    "# (checked by `argus validate`, rule tombstone_reused).\n"
)

_DROP_REASONS = {
    "intra_paper_duplicates": "Intra-paper duplicate created by the legacy append-after-reject bug (audit D1)",
    "cross_paper_duplicates": "Cross-paper duplicate: same samples reported in a companion paper or quoted as previous work (audit D3)",
    "out_of_scope": "Literature value quoted from previous work; violates the literature-comparison exclusion policy (audit D8)",
}


def _phase2_tombstones(lay: Layout) -> list[dict[str, str]]:
    import json

    path = lay.legacy / "phase2_applied_changes.json"
    if not path.exists():
        return []
    drops = json.loads(path.read_text(encoding="utf-8"))["drops"]
    out = []
    for cat, reason in _DROP_REASONS.items():
        for rid in drops.get(cat, []):
            out.append({"row_id": rid, "removed": "2026-10-14 (Phase 2)", "reason": reason})
    return sorted(out, key=lambda t: t["row_id"])


def declared_changes(lay: Layout) -> dict[str, set[str]]:
    """Row ids that post-migration curation entries declare as added/changed/removed."""
    from .build import load_side_files

    out: dict[str, set[str]] = {"rows_added": set(), "rows_changed": set(), "rows_removed": set()}
    curation, _ = load_side_files(lay)
    entries = list(curation) + [e for r in load_records(lay).records for e in r.extraction_log]
    for e in entries:
        for key in out:
            if isinstance(e.get(key), list):
                out[key].update(e[key])
    return out


def undeclared_legacy_diffs(lay: Layout) -> list[str]:
    """Differences from the frozen legacy JSONL that no curation entry declares.

    Every edit after migration must be traceable: a changed, added or removed row
    has to be listed in a curation-log entry (rows_changed / rows_added / rows_removed).
    """
    legacy = {r["row_id"]: r for r in read_jsonl(lay.legacy_rows)}
    current = {r["row_id"]: r for r in compile_rows(load_records(lay).records)}
    d = declared_changes(lay)
    out = []
    for rid in legacy.keys() - current.keys():
        if rid not in d["rows_removed"]:
            out.append(f"{rid}: removed without a declaration")
    for rid in current.keys() - legacy.keys():
        if rid not in d["rows_added"]:
            out.append(f"{rid}: added without a declaration")
    for rid in legacy.keys() & current.keys():
        changed = [c for c in COLUMN_NAMES if legacy[rid].get(c) != current[rid].get(c)]
        if changed and rid not in d["rows_changed"]:
            out.append(f"{rid}: {', '.join(changed)} changed without a declaration")
    return sorted(out)


def verify_migration(lay: Layout) -> list[str]:
    """Differences between compiled records and the legacy JSONL (empty = lossless)."""
    legacy = read_jsonl(lay.legacy_rows)
    res = load_records(lay)
    problems = [f"{p.name}: {e}" for p, e in res.errors]
    compiled = compile_rows(res.records)
    if len(compiled) != len(legacy):
        problems.append(f"row count {len(compiled)} != legacy {len(legacy)}")
    for i, (a, b) in enumerate(zip(compiled, legacy)):
        for c in COLUMN_NAMES:
            if a.get(c) != b.get(c) or type(a.get(c)) is not type(b.get(c)):
                problems.append(f"row {i} ({b.get('row_id')}) {c}: {a.get(c)!r} != {b.get(c)!r}")
    return problems
