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
    from .release import LICENSE_INFO, author_names

    meta = load_yaml(lay.data / "dataset.yaml") if (lay.data / "dataset.yaml").exists() else {}
    base = _fields(COLUMNS)
    licenses = []
    if meta.get("license"):
        title, url = LICENSE_INFO.get(meta["license"], (meta["license"], ""))
        licenses.append({"name": meta["license"], "title": title, "path": url})
    return {
        "profile": "tabular-data-package",
        "name": meta.get("name", "argus-dataset"),
        "title": "ARGUS: " + meta.get("title", "") if meta.get("title") else "",
        "version": meta.get("version", "0.0.0"),
        "created": f"{meta['released']}T00:00:00Z" if meta.get("released") else "",  # RFC 3339
        "description": meta.get("description", ""),
        "homepage": meta.get("homepage", ""),
        "licenses": licenses,
        "contributors": [{"title": n, "role": "author"} for n in author_names(meta)],
        "keywords": meta.get("keywords", []),
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
                "description": "Analysis-ready table: published columns plus derived columns. Converted or "
                               "defaulted quantities (method, direction, vol%, wt%, k_matrix) carry a *_basis "
                               "column separating reported values from conversions and defaults.",
                "schema": {"fields": base + _fields(DERIVED), "primaryKey": ["row_id"]},
            },
            {
                "name": "uncertain-measurements",
                "path": "uncertain_measurements.csv",
                "profile": "tabular-data-resource",
                "encoding": "utf-8-sig",
                "description": (f"The {counts.get('uncertain', 0)} rows of the published dataset below High "
                                "confidence (abstract-only, figure-digitized, or printed as approximate or as a "
                                "bound), with the same columns."),
                "schema": {"fields": base, "primaryKey": ["row_id"]},
            },
            {
                "name": "papers",
                "path": "paper_inventory.csv",
                "profile": "tabular-data-resource",
                "encoding": "utf-8-sig",
                "description": f"{counts.get('papers', 0)} source papers with row counts and k ranges.",
            },
            {
                "name": "extraction-log",
                "path": "extraction_log.csv",
                "profile": "tabular-data-resource",
                "encoding": "utf-8-sig",
                "description": ("Chronological extraction and curation log, one entry per paper pass: how the "
                                "source was accessed, the tables and figures inspected, QC findings and rows "
                                "rejected."),
            },
            {
                "name": "exclusions",
                "path": "unusable_sources.csv",
                "profile": "tabular-data-resource",
                "encoding": "utf-8",
                "description": ("Sources excluded at screening or extraction, with the reason. An action starting "
                                "with 'recovered' or 'abstract-recovered' means rows were later "
                                "recovered from that source after all."),
            },
        ],
    }


def descriptor_text(lay: Layout, counts: dict[str, int]) -> str:
    return json.dumps(descriptor(lay, counts), indent=2, ensure_ascii=False) + "\n"
