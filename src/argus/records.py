"""Curated per-paper records: load, save, compile to flat rows.

A record file is the unit of review: adding a paper means adding one YAML file,
and a pull request diff shows exactly which values changed and why.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from .io import atomic_write_text, dump_yaml, load_yaml
from .paths import Layout
from .schema import PaperRecord, measurement_to_row

RECORD_HEADER = (
    "# ARGUS curated extraction record: one paper, all measurements taken from it.\n"
    "# Every value must be traceable via source_location. Edit by hand or with the\n"
    "# argus CLI, then run `argus validate` and `argus build`.\n"
)

_UNSAFE = re.compile(r"[^A-Za-z0-9._-]")


def doi_slug(doi: str) -> str:
    """Filesystem-safe DOI, matching the legacy fulltext naming (10.3390_polym10030340)."""
    return _UNSAFE.sub("-", doi.replace("/", "_"))


def record_filename(paper_id: str, doi: str) -> str:
    return f"{paper_id}_{doi_slug(doi)}.yaml"


@dataclass
class LoadResult:
    records: list[PaperRecord] = field(default_factory=list)
    paths: dict[str, Path] = field(default_factory=dict)  # paper_id -> file
    errors: list[tuple[Path, str]] = field(default_factory=list)


def load_records(lay: Layout) -> LoadResult:
    """Load and structurally validate every record file, collecting all errors."""
    res = LoadResult()
    for path in sorted(lay.records.glob("*.yaml")):
        try:
            raw = load_yaml(path)
            rec = PaperRecord.model_validate(raw)
        except ValidationError as e:
            for err in e.errors():
                loc = ".".join(str(x) for x in err["loc"])
                res.errors.append((path, f"{loc}: {err['msg']}"))
            continue
        except Exception as e:  # malformed YAML
            res.errors.append((path, f"cannot parse: {e}"))
            continue
        if rec.paper_id in res.paths:
            res.errors.append((path, f"duplicate paper_id {rec.paper_id} (also {res.paths[rec.paper_id].name})"))
            continue
        res.records.append(rec)
        res.paths[rec.paper_id] = path
    return res


def record_to_dict(rec: PaperRecord) -> dict[str, Any]:
    """Serializable dict with empty/None fields dropped for compact YAML."""
    d = rec.model_dump(mode="json", exclude_none=True)
    for m in d["measurements"]:
        if not m.get("waivers"):
            m.pop("waivers", None)
    if not d["extraction_log"]:
        d.pop("extraction_log")
    return d


def save_record(lay: Layout, rec: PaperRecord, path: Path | None = None) -> Path:
    path = path or (lay.records / record_filename(rec.paper_id, rec.paper.doi))
    atomic_write_text(path, dump_yaml(record_to_dict(rec), header=RECORD_HEADER))
    return path


def compile_rows(records: list[PaperRecord]) -> list[dict[str, Any]]:
    """Flatten records (in file order) into 31-column rows."""
    rows: list[dict[str, Any]] = []
    for rec in records:
        for m in rec.measurements:
            rows.append(measurement_to_row(rec.paper, m))
    return rows


def next_paper_id(records: list[PaperRecord]) -> str:
    nums = [int(m.group(1)) for r in records if (m := re.fullmatch(r"P(\d+)", r.paper_id))]
    return f"P{(max(nums) + 1) if nums else 1:03d}"
