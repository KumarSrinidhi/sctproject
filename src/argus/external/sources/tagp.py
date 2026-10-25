"""Digitized thermal datasets from Sarikhani et al., "Unified modeling and
experimental realization of electrical and thermal percolation in polymer
composites", Appl. Phys. Rev. 9, 041403 (2022); arXiv 2209.07635 (CC BY 4.0).

Supplementary section S10 tabulates k against loading for eight literature
datasets, digitized by those authors from the source papers' figures. We keep
the two boron nitride sets (the others are carbon or metal fillers in oils and
rubbers), transcribed in tagp_thermal_datasets.csv and checked value by value
against the PDF by a second, independent reading:

  DS03  h-BN flakes / epoxy, Kargar et al. 2018 (not in ARGUS: a test set)
  DS04  BNNS aerogel / epoxy, Han et al. 2019 (ARGUS P081: a value cross-check;
        values are parallel to the lamellar layers, i.e. in-plane)

The 0 vol% point of each set is the neat matrix and gives k_matrix.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterator

from ..harmonize import ExternalRecord

KEY = "tagp"
TABLE = "tagp_thermal_datasets.csv"
DIRECTION = {"DS03": "", "DS04": "in-plane"}
SHAPE = {"DS03": "flake", "DS04": "nanosheet"}
ALIGNMENT = {"DS03": "random (high-shear mixing)", "DS04": "nacre-mimetic 3D network (aerogel infiltration)"}
YEAR = {"DS03": 2018, "DS04": 2019}  # source papers (Crossref)


def records(folder: Path) -> Iterator[ExternalRecord]:
    rows = list(csv.DictReader((folder / TABLE).open(encoding="utf-8")))
    km = {r["dataset"]: float(r["k_W_mK"]) for r in rows if float(r["vol_pct"]) == 0}
    for r in rows:
        vol = float(r["vol_pct"])
        if vol <= 0:
            continue
        ds = r["dataset"]
        yield ExternalRecord(
            source=KEY, ext_id=f"{ds}#{r['point']}", k=float(r["k_W_mK"]),
            filler=r["filler"], matrix=r["matrix"], doi=r["source_doi"], vol_pct=vol,
            wt_pct=float(r["wt_pct"]) if r["wt_pct"] else None, k_matrix=km.get(ds),
            direction=DIRECTION.get(ds, ""), shape=SHAPE.get(ds, ""), alignment=ALIGNMENT.get(ds, ""),
            processing=r["fabrication"], title=r["source_title"], year=YEAR.get(ds),
            value_source="figure",  # digitized from the source paper's figure
            notes=f"Digitized by Sarikhani et al. (2022), dataset {ds}, from {r['selected_figure']}.",
            extra={"dataset": ds},
        )
