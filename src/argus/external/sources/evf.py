"""EVF_Thermal_Conductivity_Dataset (Anastasiou 2026, figshare, CC BY 4.0).

Sheet1 holds one row per data point with the series name, nominal volume
fraction (as a fraction), measured composite k, matrix k, intrinsic filler k
and the source citation. Only the polymer + ceramic series listed under
`include` in data/external/evf/series_map.yaml are used; every other series is
listed under `exclude` with its reason, and an unmapped series is an error.

The workbook also carries the author's own Maxwell, Bruggeman, Hill and Nan
predictions per point; `model_columns` exposes them for the implementation
cross-check in argus.external.physics_check.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

from ...io import load_yaml
from ..harmonize import ExternalRecord

KEY = "evf"
WORKBOOK = "raw/EVF_Thermal_Conductivity_Dataset.xlsx"
SHEET = "Sheet1"
MODEL_COLUMNS = {"hill": "M0_Hill", "maxwell": "M1_Maxwell", "bruggeman": "M2_Bruggeman", "nan": "M3_Nan"}


class MappingError(ValueError):
    pass


@dataclass(frozen=True)
class EvfPoint:
    series: str
    index: int            # position of the point within its series (0-based, workbook order)
    raw: dict[str, Any]   # the workbook row, column name -> value


def _f(v: Any) -> float | None:
    if v is None or isinstance(v, bool):
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def read_points(folder: Path) -> list[EvfPoint]:
    try:
        import openpyxl
    except ImportError as e:  # pragma: no cover - exercised only without the extra
        raise ImportError("reading the EVF workbook needs openpyxl: pip install -e '.[external]'") from e
    wb = openpyxl.load_workbook(folder / WORKBOOK, read_only=True, data_only=True)
    try:
        rows = list(wb[SHEET].iter_rows(values_only=True))
    finally:
        wb.close()
    head = [str(h).strip() if h is not None else "" for h in rows[0]]
    out, seen = [], {}
    for r in rows[1:]:
        d = dict(zip(head, r))
        s = d.get("Composite_Series")
        if not s:
            continue
        i = seen.get(s, 0)
        seen[s] = i + 1
        out.append(EvfPoint(series=str(s), index=i, raw=d))
    return out


def load_map(folder: Path) -> dict[str, Any]:
    m = load_yaml(folder / "series_map.yaml") or {}
    return {"include": m.get("include") or {}, "exclude": m.get("exclude") or {}}


def check_map(points: list[EvfPoint], mapping: dict[str, Any]) -> None:
    series = {p.series for p in points}
    inc, exc = set(mapping["include"]), set(mapping["exclude"])
    problems = []
    if inc & exc:
        problems.append(f"both included and excluded: {sorted(inc & exc)}")
    if series - inc - exc:
        problems.append(f"unmapped series: {sorted(series - inc - exc)}")
    if (inc | exc) - series:
        problems.append(f"mapped series missing from the workbook: {sorted((inc | exc) - series)}")
    if problems:
        raise MappingError("; ".join(problems))


def records(folder: Path) -> Iterator[ExternalRecord]:
    """Test points: included series, loading > 0."""
    points = read_points(folder)
    mapping = load_map(folder)
    check_map(points, mapping)
    for p in points:
        spec = mapping["include"].get(p.series)
        if spec is None:
            continue
        vf, k, km = _f(p.raw.get("Vf")), _f(p.raw.get("k_exp_WmK")), _f(p.raw.get("k_matrix_WmK"))
        if vf is None or k is None or vf <= 0:
            continue
        temp = spec.get("temperature_C", _f(p.raw.get("Temperature_C")))
        fig = str(p.raw.get("Figure/Table") or "").lower()
        yield ExternalRecord(
            source=KEY,
            ext_id=f"{p.series}#{p.index}",
            k=k,
            filler=spec["filler"],
            matrix=spec["matrix"],
            doi=spec.get("doi", ""),
            group=spec.get("paper", ""),
            vol_pct=round(vf * 100.0, 6),
            k_matrix=km,
            method=spec.get("method") or str(p.raw.get("Measurement_method") or ""),
            direction=spec.get("direction", ""),
            size_um=spec.get("size_um"),
            shape=spec.get("shape", ""),
            treatment=spec.get("treatment", ""),
            alignment=spec.get("alignment", ""),
            processing=spec.get("processing", ""),
            temperature_C=temp,
            year=spec.get("year"),
            # every included series cites a figure of its source (digitized by EVF)
            value_source="figure" if "fig" in fig else "table" if "table" in fig else "",
            title=str(p.raw.get("Citation") or ""),
            notes=f"EVF series {p.series}. {spec.get('notes', '')}".strip(),
            extra={"series": p.series, "k_filler_evf": _f(p.raw.get("k_filler_WmK")),
                   "figure": str(p.raw.get("Figure/Table") or "")},
        )


def zero_loading_check(folder: Path) -> list[dict[str, Any]]:
    """For included series with a Vf = 0 point: does that point equal the series' k_matrix?"""
    mapping = load_map(folder)
    out = []
    for p in read_points(folder):
        if p.series in mapping["include"] and _f(p.raw.get("Vf")) == 0:
            k0, km = _f(p.raw.get("k_exp_WmK")), _f(p.raw.get("k_matrix_WmK"))
            if k0 is not None and km:
                out.append({"series": p.series, "k_at_zero": k0, "k_matrix": km, "rel_diff": round(k0 / km - 1, 4)})
    return out


def model_columns(folder: Path) -> list[dict[str, Any]]:
    """Per included point: inputs (phi, km, kf, radius, R) and EVF's own model predictions."""
    mapping = load_map(folder)
    out = []
    for p in read_points(folder):
        if p.series not in mapping["include"]:
            continue
        vf = _f(p.raw.get("Vf"))
        if vf is None or vf <= 0:
            continue
        row = {"series": p.series, "index": p.index, "phi": vf,
               "km": _f(p.raw.get("k_matrix_WmK")), "kf": _f(p.raw.get("k_filler_WmK")),
               "k_exp": _f(p.raw.get("k_exp_WmK")), "radius_m": _f(p.raw.get("particle_radius_m")),
               "r_bd": _f(p.raw.get("RBd_m2K_W")), "alpha_nan": _f(p.raw.get("alpha_Nan"))}
        row.update({name: _f(p.raw.get(col)) for name, col in MODEL_COLUMNS.items()})
        out.append(row)
    return out
