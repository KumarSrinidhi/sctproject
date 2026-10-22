"""Frictionless Data Package descriptor (datapackage.json, v1-compatible).

Kept at spec v1 on purpose: v2 (2024) readers were not yet available in the
Python/R libraries as of early 2026 (research report, tooling section).
"""
from __future__ import annotations

import json
from typing import Any

from .enrich import DERIVED
from .io import load_yaml
from .paths import Layout
from .schema import COLUMNS

_TYPES = {"string": "string", "number": "number", "integer": "integer", "boolean": "boolean"}


def _fields(cols) -> list[dict[str, Any]]:
    out = []
    for c in cols:
        f = {"name": c.name, "type": _TYPES[c.kind], "description": c.description}
        if getattr(c, "unit", ""):
            f["unit"] = c.unit
        out.append(f)
    return out


def descriptor(lay: Layout, counts: dict[str, int]) -> dict[str, Any]:
    meta = load_yaml(lay.data / "dataset.yaml") if (lay.data / "dataset.yaml").exists() else {}
    base = _fields(COLUMNS)
    return {
        "profile": "tabular-data-package",
        "name": meta.get("name", "argus-dataset"),
        "title": meta.get("title", ""),
        "version": meta.get("version", "0.0.0"),
        "created": meta.get("released", ""),
        "description": meta.get("description", ""),
        "homepage": meta.get("homepage", ""),
        "resources": [
            {
                "name": "measurements",
                "path": "thermal_conductivity_dataset.csv",
                "profile": "tabular-data-resource",
                "encoding": "utf-8-sig",
                "description": f"Published dataset, {counts.get('rows', 0)} rows: one measured k per row.",
                "schema": {"fields": base, "primaryKey": ["row_id"]},
            },
            {
                "name": "measurements-enriched",
                "path": "data/processed/measurements_enriched.csv",
                "profile": "tabular-data-resource",
                "encoding": "utf-8-sig",
                "description": "Analysis-ready table: published columns plus derived columns, each with a *_basis "
                               "column separating reported values from conversions and defaults.",
                "schema": {"fields": base + _fields(DERIVED), "primaryKey": ["row_id"]},
            },
            {
                "name": "papers",
                "path": "paper_inventory.csv",
                "profile": "tabular-data-resource",
                "encoding": "utf-8-sig",
                "description": f"{counts.get('papers', 0)} source papers with row counts and k ranges.",
            },
            {
                "name": "exclusions",
                "path": "unusable_sources.csv",
                "profile": "tabular-data-resource",
                "encoding": "utf-8",
                "description": "Screened sources that contribute no rows, with the reason.",
            },
        ],
    }


def descriptor_text(lay: Layout, counts: dict[str, int]) -> str:
    return json.dumps(descriptor(lay, counts), indent=2, ensure_ascii=False) + "\n"
