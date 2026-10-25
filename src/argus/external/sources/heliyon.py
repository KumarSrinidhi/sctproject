"""Table 1 of Mumtaz et al., Heliyon 10, e25381 (2024; CC BY-NC-ND 4.0), a
review's summary of recent high-k composites.

Only the rows whose source paper is also in ARGUS are kept (shared_rows.csv:
the reported facts with attribution, not a copy of the table). A row quoting
k-parallel and k-perpendicular becomes two values. The review gives no matrix
k, so these rows serve the value cross-check only.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from ..harmonize import ExternalRecord

KEY = "heliyon"
TABLE = "shared_rows.csv"


def records(folder: Path) -> Iterator[ExternalRecord]:
    for i, r in enumerate(csv.DictReader((folder / TABLE).open(encoding="utf-8"))):
        yield ExternalRecord(
            source=KEY, ext_id=f"row{r['table_row']}-{r['direction']}", k=float(r["k_W_mK"]),
            filler=r["filler"], matrix=r["matrix"], doi=r["ref_doi"], vol_pct=float(r["vol_pct"]),
            direction=r["direction"], processing=r["technique"], year=int(r["year"]) if r.get("year") else None,
            value_source="table",
            notes=f"Mumtaz et al. 2024, Table 1 row {r['table_row']} ({r['loading_text']}), ref. {r['ref_number']}.",
        )
