"""Project layout. Every path the toolkit touches is defined here."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def find_root(start: Path | None = None) -> Path:
    """Walk up from `start` (default: cwd) to the folder holding pyproject.toml."""
    env = os.environ.get("ARGUS_ROOT")
    if env:
        return Path(env).resolve()
    here = (start or Path.cwd()).resolve()
    for p in (here, *here.parents):
        if (p / "pyproject.toml").exists() and (p / "data").is_dir():
            return p
    # Fall back to the repo that contains this package (src/argus/paths.py).
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class Layout:
    root: Path

    # --- curated inputs (source of truth) ---
    @property
    def data(self) -> Path:
        return self.root / "data"

    @property
    def records(self) -> Path:
        return self.data / "records"

    @property
    def curation_log(self) -> Path:
        return self.data / "curation_log.yaml"

    @property
    def exclusions(self) -> Path:
        return self.data / "exclusions.yaml"

    @property
    def tombstones(self) -> Path:
        return self.data / "tombstones.yaml"

    # --- generated outputs ---
    @property
    def processed(self) -> Path:
        return self.data / "processed"

    @property
    def compiled_jsonl(self) -> Path:
        return self.processed / "rows.jsonl"

    @property
    def reports(self) -> Path:
        return self.root / "reports"

    # Published deliverables keep their historical names at the repo root.
    @property
    def dataset_csv(self) -> Path:
        return self.root / "thermal_conductivity_dataset.csv"

    @property
    def inventory_csv(self) -> Path:
        return self.root / "paper_inventory.csv"

    @property
    def log_csv(self) -> Path:
        return self.root / "extraction_log.csv"

    @property
    def uncertain_csv(self) -> Path:
        return self.root / "uncertain_measurements.csv"

    @property
    def unusable_csv(self) -> Path:
        return self.root / "unusable_sources.csv"

    # --- legacy pipeline (frozen, read-only) ---
    @property
    def legacy(self) -> Path:
        return self.root / "work"

    @property
    def legacy_rows(self) -> Path:
        return self.legacy / "rows_raw.jsonl"

    @property
    def legacy_log(self) -> Path:
        return self.legacy / "extraction_log.jsonl"

    @property
    def fulltext(self) -> Path:
        return self.legacy / "fulltext"


def layout(root: Path | None = None) -> Layout:
    return Layout(root.resolve() if root else find_root())
