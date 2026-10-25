"""Turn checked extractions into ARGUS record files.

Input per paper: the extractor's rows and the independent verifier's verdict on
each (accept / fix / reject) plus rows the verifier found missing. A row enters
a record only if, after the verifier's corrections:
  * its quote occurs verbatim in the cached source text, and
  * the printed k value appears in that quote.
Rows the verifier added are held to the same two checks and labelled in notes.
Papers without usable rows become exclusions with a reason.
"""
from __future__ import annotations

import datetime as _dt
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ..io import dump_yaml, load_yaml
from ..paths import Layout
from ..records import doi_slug, load_records, next_paper_id, save_record
from ..schema import Measurement, PaperMeta, PaperRecord
from ..validate import doi_hash
from .quotes import approximate_k, number_in_quote, quote_in_source

MEASUREMENT_FIELDS = set(Measurement.model_fields) - {"row_id", "waivers"}


@dataclass
class ImportReport:
    created: list[str] = field(default_factory=list)       # paper ids
    excluded: list[tuple[str, str]] = field(default_factory=list)  # (doi, reason)
    rows_added: int = 0
    rejected: list[tuple[str, int, str]] = field(default_factory=list)  # (doi, index, reason)


def _merge_rows(ext_rows: list[dict[str, Any]], verdict: dict[str, Any] | None) -> tuple[list[dict], list[tuple[int, str]]]:
    by_idx = {v["index"]: v for v in (verdict or {}).get("rows", [])}
    keep, rejected = [], []
    for i, r in enumerate(ext_rows):
        v = by_idx.get(i)
        if v is None:
            rejected.append((i, "no verifier verdict"))
            continue
        if v["verdict"] == "reject":
            rejected.append((i, f"verifier: {v.get('reason', '')}"))
            continue
        row = dict(r)
        if v["verdict"] == "fix":
            row.update({k: val for k, val in (v.get("corrections") or {}).items() if k in MEASUREMENT_FIELDS | {"quote", "location"}})
            row["_fixed"] = v.get("reason", "")
        keep.append(row)
    for r in (verdict or {}).get("missed", []):
        keep.append({**r, "_added_by_verifier": True})
    return keep, rejected


def _checked(row: dict[str, Any], text: str) -> str | None:
    """None if the row passes the provenance checks, else the reason."""
    if not quote_in_source(row.get("quote", ""), text):
        return "quote not found verbatim in the source"
    if not number_in_quote(float(row["k_original_value"]), row["quote"]):
        return "printed k value not in its quote"
    return None


def build_measurement(row: dict[str, Any], row_id: str) -> Measurement:
    data = {k: row.get(k) for k in MEASUREMENT_FIELDS if row.get(k) is not None}
    loc = row.get("location") or ("Table" if row.get("value_source") == "table" else "Text")
    data["source_location"] = f"{loc}: '{row['quote']}'"
    notes = [row.get("notes") or ""]
    if row.get("_added_by_verifier"):
        notes.append("Row found by the independent verifier (extractor had missed it); quote checked.")
    if row.get("_fixed"):
        notes.append(f"Corrected in verification: {row['_fixed']}")
    if approximate_k(float(row["k_original_value"]), row["quote"]) and data.get("confidence") == "High":
        data["confidence"] = "Medium"  # house rule: approximate or bounded values are never High
        notes.append("k printed as approximate or as a bound, so Medium confidence.")
    data["notes"] = " ".join(n for n in notes if n).strip() or None
    return Measurement(row_id=row_id, **data)


def import_batch(lay: Layout, papers: list[dict[str, Any]], verdicts: dict[str, dict[str, Any]],
                 meta: dict[str, dict[str, Any]], text_dir: Path, date: str | None = None,
                 dry_run: bool = False) -> ImportReport:
    """papers: extractor output entries; verdicts: doi -> verifier entry; meta: doi -> {title, year, license}."""
    date = date or _dt.date.today().isoformat()
    res = load_records(lay)
    records = list(res.records)
    from ..build import tombstone_ids

    used = [int(m.row_id.split("-")[1]) for r in records for m in r.measurements]
    used += [int(t.split("-")[1]) for t in tombstone_ids(lay)]  # removed ids are never reused
    seq = max(used, default=0) + 1
    curation = (load_yaml(lay.curation_log) or {}).get("entries", []) if lay.curation_log.exists() else []
    log_seq = max([e.get("seq", 0) for r in records for e in r.extraction_log] +
                  [e.get("seq", 0) for e in curation], default=0) + 1
    known = {r.paper.doi.lower() for r in records}
    rep = ImportReport()
    for p in papers:
        doi = p["doi"].lower()
        if doi in known:
            rep.excluded.append((doi, "already has a record"))
            continue
        v = verdicts.get(doi)
        text = (text_dir / f"{doi_slug(doi)}.txt").read_text(encoding="utf-8")
        if not p.get("usable") or (v and not v.get("usable_agreed", True) and not v.get("missed")):
            why = p.get("reason_if_not_usable") or (v or {}).get("notes", "") or "no printed BN/AlN composite k values"
            rep.excluded.append((doi, f"Phase 6 screening of full text: {why}"[:300]))
            continue
        rows, rejected = _merge_rows(p.get("measurements", []), v)
        good = []
        for i, r in enumerate(rows):
            why = _checked(r, text)
            if why:
                rejected.append((i, why))
            else:
                good.append(r)
        for i, why in rejected:
            rep.rejected.append((doi, i, why))
        if not good:
            rep.excluded.append((doi, "Phase 6: no row passed verification and the provenance checks"))
            continue
        pid = next_paper_id(records)
        h = doi_hash(doi)
        ms = []
        for r in good:
            ms.append(build_measurement(r, f"{h}-{seq:03d}"))
            seq += 1
        m = meta.get(doi, {})
        log = {"seq": log_seq, "candidate_id": f"P6-{pid}", "doi": doi,
               "paper_title": m.get("title") or p.get("title_as_printed", ""), "date_processed": date,
               "access_result": f"Europe PMC JATS full text (OA; {m.get('license') or 'licence in JATS'})",
               "files_inspected": f"sources/text/{doi_slug(doi)}.txt (cache, not committed)",
               "tables_inspected": p.get("tables_inspected", ""), "figures_inspected": p.get("figures_inspected", ""),
               "candidate_measurements": len(p.get("measurements", [])) + len((v or {}).get("missed", [])),
               "rows_appended": len(ms), "unit_conversions": "none (values as printed)",
               "duplicate_checks": "new DOI; no prior rows",
               "qc_findings": (f"Extracted by one agent, every row checked against the source by an independent verifier; "
                               f"quotes verified verbatim; {p.get('figure_only_skipped', 0)} figure-only values not taken. "
                               + (p.get("extraction_notes") or ""))[:600],
               "rows_rejected_at_append": [[f"{h}-candidate-{i}", why] for i, why in rejected],
               # declares the additions for `argus verify` (changes_declared)
               "rows_added": [m_.row_id for m_ in ms]}
        log_seq += 1
        rec = PaperRecord(paper_id=pid, paper=PaperMeta(doi=doi, title=m.get("title") or p["title_as_printed"],
                                                       year=int(m.get("year") or p["year"]), source_url=f"https://doi.org/{doi}"),
                          extraction_log=[log], measurements=ms)
        records.append(rec)
        known.add(doi)
        rep.created.append(pid)
        rep.rows_added += len(ms)
        if not dry_run:
            save_record(lay, rec)
    if rep.excluded and not dry_run:
        add_exclusions(lay, rep.excluded)
    return rep


def add_exclusions(lay: Layout, items: list[tuple[str, str]]) -> None:
    """Append new exclusions (existing entries are left byte-for-byte as they are)."""
    data = (load_yaml(lay.exclusions) if lay.exclusions.exists() else None) or {"exclusions": []}
    have = {str(e["doi"]).lower() for e in data.get("exclusions") or []}
    new = [{"doi": doi, "reason": reason, "action": "unusable"} for doi, reason in items
           if doi not in have and reason != "already has a record"]
    if not new:
        return
    text = lay.exclusions.read_text(encoding="utf-8") if lay.exclusions.exists() else "exclusions:\n"
    block = dump_yaml(new)
    if not text.endswith("\n"):
        text += "\n"
    lay.exclusions.write_text(text + block, encoding="utf-8")
