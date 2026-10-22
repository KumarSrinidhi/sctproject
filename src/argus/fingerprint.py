"""Dataset fingerprint: ties every analysis output to the exact data it used.

Analyses (`argus physics`, `argus analyze bias`, `argus ml benchmark`) stamp
their JSON with this block; the course report refuses to render from an
output whose fingerprint does not match the current records.
"""
from __future__ import annotations

import hashlib
from typing import Any

from .io import jsonl_text
from .records import compile_rows
from .schema import PaperRecord


def dataset_fingerprint(records: list[PaperRecord]) -> dict[str, Any]:
    rows = compile_rows(records)
    digest = hashlib.sha256(jsonl_text(rows).encode("utf-8")).hexdigest()
    return {"rows": len(rows), "papers": len({r["doi"] for r in rows}), "sha256": digest[:16]}


class StaleAnalysis(RuntimeError):
    pass


def check_fresh(name: str, output: dict[str, Any], current: dict[str, Any], command: str) -> None:
    got = (output or {}).get("dataset", {}).get("sha256")
    if got != current["sha256"]:
        raise StaleAnalysis(f"{name} was computed from different data (fingerprint {got or 'missing'} vs current "
                            f"{current['sha256']}); re-run `{command}` first")
