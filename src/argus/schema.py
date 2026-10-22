"""Data model.

Two shapes of the same data:

* **Record** (`PaperRecord`): one YAML file per paper under data/records/. Paper
  metadata is stated once; each measurement lists only the fields it has.
* **Row**: the flat 31-column layout of thermal_conductivity_dataset.csv. Empty
  fields are '' (the historical convention, kept so outputs stay byte-stable).

Structural typing lives here (pydantic). Scientific and policy rules
(k > 0, provenance present, figure rows not High, ...) live in validate.py so
that every problem in a file is reported at once rather than the first one.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Column:
    name: str
    kind: Literal["string", "number", "integer"]
    level: Literal["paper", "measurement"]
    description: str
    unit: str = ""


COLUMNS: tuple[Column, ...] = (
    Column("row_id", "string", "measurement", "Stable row identifier: md5(doi)[:8] + '-' + sequence number."),
    Column("doi", "string", "paper", "DOI of the source paper (lower-case, no URL prefix)."),
    Column("source_url", "string", "paper", "Resolvable URL of the source paper."),
    Column("paper_title", "string", "paper", "Title of the source paper (Crossref-verified where audited)."),
    Column("year", "integer", "paper", "Publication year."),
    Column("matrix_polymer", "string", "measurement", "Matrix polymer as described by the source."),
    Column("curing_agent", "string", "measurement", "Hardener / curing agent, if stated."),
    Column("filler_material", "string", "measurement", "Normalized filler label (h-BN, BN, BNNS, AlN, cBN, '<a>/<b> hybrid', none)."),
    Column("filler_material_original", "string", "measurement", "Filler name verbatim from the source."),
    Column("filler_shape", "string", "measurement", "Filler morphology (platelet, nanosheet, particle, sphere, ...)."),
    Column("filler_aspect_ratio", "number", "measurement", "Filler aspect ratio, if stated."),
    Column("filler_mean_size_um", "number", "measurement", "Mean (lateral) filler size.", "um"),
    Column("size_distribution", "string", "measurement", "Size distribution description, if stated."),
    Column("filler_loading_vol_pct", "number", "measurement", "Filler loading, volume percent, as reported.", "vol%"),
    Column("filler_loading_wt_pct", "number", "measurement", "Filler loading, weight percent, as reported.", "wt%"),
    Column("filler_loading_original_value", "string", "measurement", "Loading value as printed in the source (may be non-numeric, e.g. '44-45')."),
    Column("filler_loading_original_unit", "string", "measurement", "Unit / basis of the printed loading."),
    Column("functionalization", "string", "measurement", "Surface treatment of the filler."),
    Column("filler_alignment", "string", "measurement", "Filler orientation / network structure."),
    Column("processing_method", "string", "measurement", "Composite processing route."),
    Column("k_matrix_W_mK", "number", "measurement", "Thermal conductivity of the neat matrix.", "W/(m K)"),
    Column("k_composite_W_mK", "number", "measurement", "Effective thermal conductivity of the composite (normalized).", "W/(m K)"),
    Column("k_direction", "string", "measurement", "Direction measured (in-plane / through-plane / unknown) as reported."),
    Column("measurement_method", "string", "measurement", "Measurement technique / instrument as described by the source."),
    Column("measurement_temperature_C", "number", "measurement", "Measurement temperature; blank means ambient (~25 C).", "C"),
    Column("k_original_value", "number", "measurement", "k value as printed in the source."),
    Column("k_original_unit", "string", "measurement", "Unit of k as printed in the source."),
    Column("value_source", "string", "measurement", "Where the value came from: text | table | figure."),
    Column("source_location", "string", "measurement", "Verbatim quote, table id or figure + digitizer reference."),
    Column("confidence", "string", "measurement", "High | Medium (| Low)."),
    Column("notes", "string", "measurement", "Caveats, sample labels, hybrid composition."),
)

COLUMN_NAMES: tuple[str, ...] = tuple(c.name for c in COLUMNS)
BY_NAME: dict[str, Column] = {c.name: c for c in COLUMNS}
PAPER_COLUMNS: tuple[str, ...] = tuple(c.name for c in COLUMNS if c.level == "paper")
MEASUREMENT_COLUMNS: tuple[str, ...] = tuple(c.name for c in COLUMNS if c.level == "measurement")
NUMERIC_COLUMNS: frozenset[str] = frozenset(c.name for c in COLUMNS if c.kind == "number")

VALUE_SOURCES = ("text", "table", "figure")
CONFIDENCE_LEVELS = ("High", "Medium", "Low")


# --------------------------------------------------------------------------- record model

Num = float | None


class Waiver(BaseModel):
    """An explicit, reviewed exception to one validation rule for one row."""

    model_config = ConfigDict(extra="forbid")
    rule: str
    reason: str


class Measurement(BaseModel):
    """One measured k value. Field names match the published CSV columns."""

    model_config = ConfigDict(extra="forbid")

    row_id: str
    matrix_polymer: str | None = None
    curing_agent: str | None = None
    filler_material: str | None = None
    filler_material_original: str | None = None
    filler_shape: str | None = None
    filler_aspect_ratio: Num = None
    filler_mean_size_um: Num = None
    size_distribution: str | None = None
    filler_loading_vol_pct: Num = None
    filler_loading_wt_pct: Num = None
    filler_loading_original_value: float | str | None = None
    filler_loading_original_unit: str | None = None
    functionalization: str | None = None
    filler_alignment: str | None = None
    processing_method: str | None = None
    k_matrix_W_mK: Num = None
    k_composite_W_mK: Num = None
    k_direction: str | None = None
    measurement_method: str | None = None
    measurement_temperature_C: Num = None
    k_original_value: Num = None
    k_original_unit: str | None = None
    value_source: str | None = None
    source_location: str | None = None
    confidence: str | None = None
    notes: str | None = None
    waivers: list[Waiver] = Field(default_factory=list)


class PaperMeta(BaseModel):
    model_config = ConfigDict(extra="forbid")
    doi: str
    title: str
    year: int | None = None
    source_url: str | None = None


class PaperRecord(BaseModel):
    """Contents of one data/records/P###_*.yaml file."""

    model_config = ConfigDict(extra="forbid")
    schema_version: int = SCHEMA_VERSION
    paper_id: str
    paper: PaperMeta
    extraction_log: list[dict[str, Any]] = Field(default_factory=list)
    measurements: list[Measurement] = Field(default_factory=list)


# --------------------------------------------------------------------------- row helpers

def empty_row() -> dict[str, Any]:
    return {c: "" for c in COLUMN_NAMES}


def measurement_to_row(paper: PaperMeta, m: Measurement) -> dict[str, Any]:
    """Flatten a measurement into the 31-column row (missing -> '')."""
    row = empty_row()
    row.update(
        doi=paper.doi,
        source_url=paper.source_url or "",
        paper_title=paper.title,
        year=paper.year if paper.year is not None else "",
    )
    for name in MEASUREMENT_COLUMNS:
        v = getattr(m, name)
        row[name] = "" if v is None else v
    return row


def row_to_measurement_fields(row: dict[str, Any]) -> dict[str, Any]:
    """Inverse of measurement_to_row for the measurement-level fields ('' dropped)."""
    return {k: row[k] for k in MEASUREMENT_COLUMNS if row.get(k, "") not in ("", None)}
