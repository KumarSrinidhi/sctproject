"""Source data of He, Wu & Fu, "Thermal conductivity modeling beyond the dilute
limit" (Nature Communications 2025; figshare 10.6084/m9.figshare.30426895, MIT).

Sheet "SI_fig12-18" lists 242 measured composites by numbers only (km, kf,
particle diameter 2r, loading, measured k and the authors' fitted interfacial
resistance Ri) together with each model's deviation delta = k_model - k_measured
for the BCC, Bruggeman, Hasselman-Johnson, Maxwell-Garnett, S-P and simple-cubic
models. There are no material names or sources per row, so these points serve
the physics checks only, never the ML or the value cross-check.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

KEY = "bcc"
WORKBOOK = "raw/Source data NCOMMS-25-36881A.xlsx"
SHEET = "SI_fig12-18"
# column index in SI_fig12-18 -> name
INPUTS = {0: "km", 1: "kf", 2: "diameter_m", 3: "k_exp", 4: "vf_pct", 5: "r_i"}
DELTAS = {7: "bcc", 9: "bruggeman", 11: "hasselman_johnson", 13: "maxwell_garnett", 15: "s_p", 17: "simple_cubic"}


def _f(v: Any) -> float | None:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def points(folder: Path) -> list[dict[str, Any]]:
    """One dict per measured point: inputs, phi (fraction), and each model's predicted k."""
    try:
        import openpyxl
    except ImportError as e:  # pragma: no cover
        raise ImportError("reading the BCC workbook needs openpyxl: pip install -e '.[external]'") from e
    wb = openpyxl.load_workbook(folder / WORKBOOK, read_only=True, data_only=True)
    try:
        rows = list(wb[SHEET].iter_rows(values_only=True))
    finally:
        wb.close()
    out = []
    for i, r in enumerate(rows[1:], start=2):
        vals = {name: _f(r[c]) for c, name in INPUTS.items()}
        if any(v is None for v in vals.values()):
            continue
        p = {"sheet_row": i, **vals, "phi": vals["vf_pct"] / 100.0, "radius_m": vals["diameter_m"] / 2.0}
        p["model"] = {name: (d + vals["k_exp"]) if (d := _f(r[c])) is not None else None for c, name in DELTAS.items()}
        out.append(p)
    return out
