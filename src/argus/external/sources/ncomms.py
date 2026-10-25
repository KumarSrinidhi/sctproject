"""Supplementary Data 1 of He, Wu & Fu, "Thermal conductivity modeling beyond the
dilute limit", Nat. Commun. (2025), doi 10.1038/s41467-025-67013-y.

The labelled version of the BCC validation set: each block of rows shares a
'Systems' label (filler-matrix plus the k method), with measured k, volume and
weight fraction, particle diameter, km, kf and a fitted interfacial resistance
per row. The article (and so this file) is CC BY-NC-ND 4.0: we may use it for
non-commercial validation but not redistribute a modified copy, so the xlsx is
downloaded by `argus external fetch ncomms` and never committed. Our own
curation (which block is which paper, which blocks are used) is in
block_map.yaml.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Iterator

from ...io import load_yaml
from ..harmonize import ExternalRecord

KEY = "ncomms"
WORKBOOK = "raw/41467_2025_67013_MOESM3_ESM.xlsx"
COLS = ("label", "ka", "vf", "wf", "diameter_m", "km", "kf", "ri")


class MappingError(ValueError):
    pass


def _f(v: Any) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def sheet_rows(folder: Path) -> dict[int, dict[str, Any]]:
    try:
        import openpyxl
    except ImportError as e:  # pragma: no cover
        raise ImportError("reading the workbook needs openpyxl: pip install -e '.[external]'") from e
    path = folder / WORKBOOK
    if not path.exists():
        raise FileNotFoundError(2, "not fetched", str(path))
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    try:
        rows = list(wb.worksheets[0].iter_rows(values_only=True))
    finally:
        wb.close()
    return {i: dict(zip(COLS, r)) for i, r in enumerate(rows, start=1) if i > 2}


def load_map(folder: Path) -> dict[int, dict[str, Any]]:
    return {int(k): v for k, v in ((load_yaml(folder / "block_map.yaml") or {}).get("blocks") or {}).items()}


def check_map(rows: dict[int, dict[str, Any]], blocks: dict[int, dict[str, Any]]) -> None:
    """Blocks must tile the data rows exactly, and each block's first row must carry its label."""
    covered = sorted(i for b in blocks.values() for i in range(b["rows"][0], b["rows"][1] + 1))
    data_rows = sorted(i for i, r in rows.items() if _f(r["ka"]) is not None)
    if covered != data_rows:
        raise MappingError("block_map.yaml does not tile the data rows of the workbook")
    for n, b in blocks.items():
        first = str(rows[b["rows"][0]]["label"] or "").replace("\n", " | ").strip()
        if first != b["label"]:
            raise MappingError(f"block {n}: workbook label {first!r} != map label {b['label']!r}")


def records(folder: Path) -> Iterator[ExternalRecord]:
    rows = sheet_rows(folder)
    blocks = load_map(folder)
    check_map(rows, blocks)
    for n, b in sorted(blocks.items()):
        if b["use"] != "test":
            continue
        skip = {int(k) for k in (b.get("exclude_rows") or {})}
        for i in range(b["rows"][0], b["rows"][1] + 1):
            if i in skip:
                continue
            r = rows[i]
            ka, vf, wf, d, km = (_f(r[c]) for c in ("ka", "vf", "wf", "diameter_m", "km"))
            if ka is None or vf is None or vf <= 0:
                continue
            yield ExternalRecord(
                source=KEY, ext_id=f"block{n}#row{i}", k=ka, filler=b["filler"], matrix=b["matrix"],
                doi=b["doi"], group=b.get("paper", ""), vol_pct=round(vf * 100, 6),
                wt_pct=round(wf * 100, 6) if wf is not None else None, k_matrix=km,
                method=b["method"], size_um=d * 1e6 if d else None, shape=b.get("shape", ""),
                treatment=b.get("treatment", ""), alignment=b.get("alignment", ""), year=b.get("year"),
                value_source="",  # the compilation does not say whether values came from tables or figures
                title=b["label"], notes=f"Nat. Commun. 2025 Supplementary Data 1, block {n} ({b['label']}).",
                extra={"block": n, "own_work": bool(b.get("own_work"))},
            )
