"""Interactive data explorer: one self-contained HTML page, no external scripts.

Two variants from one template:
  docs/explorer/index.html            standalone document (open locally, Pages)
  docs/explorer/explorer.artifact.html  page fragment for publishing as an
                                       Artifact (the host adds doctype/head/body)

The page embeds the enriched rows, Nan 1997 / Maxwell reference curves and
the dataset fingerprint. All strings are rendered client-side with
textContent; the JSON is escaped so it cannot close its <script> element.
"""
from __future__ import annotations

import datetime as _dt
import json
import math
from importlib import resources
from pathlib import Path
from typing import Any

import numpy as np

from ..enrich import enrich_records
from ..fingerprint import check_fresh, dataset_fingerprint
from ..io import atomic_write_text, load_yaml
from ..paths import Layout
from ..physics.emt import maxwell_limit_ratio, nan1997
from ..records import load_records
from ..vocab import METHOD_CLASSES, filler_props

KM_REF = 0.2  # epoxy, W/(m K): reference matrix for the model curves
SIZE_REF_UM = 10.0

# Filter groups (chips) and colour-by groupings (at most three groups each:
# the validated palette clears all-pairs colour-blind checks only for three).
FILLER_FILTER = {"h-BN": "hBN", "BN": "hBN", "BNNS": "BNNS", "AlN": "AlN", "Al2O3": "oxide", "MgO": "oxide",
                 "cBN": "oxide"}
METHOD_FILTER = {"LFA": "LFA", "TPS": "TPS", "THB": "THB", "HOT_WIRE": "HOT_WIRE", "MTPS": "TPS",
                 "SS_D5470": "STEADY", "SS_GHFM": "STEADY", "SS_HFM_GHP": "STEADY", "SS_UNSPECIFIED": "STEADY",
                 "PERIODIC": "OTHER", "THIN_FILM": "OTHER", "IR_THERMO": "OTHER", "UNSPECIFIED": "UNSPECIFIED"}


def _f(v: Any) -> float | None:
    if isinstance(v, bool) or v in (None, ""):
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def filler_group(r: dict[str, Any]) -> str:
    if r["is_hybrid"] in (True, "true"):
        return "hybrid"
    if r["filler_family"] == "none" or not r["filler_base"]:
        return "neat"
    return FILLER_FILTER.get(r["filler_base"], "oxide")


def provenance_group(r: dict[str, Any]) -> str:
    flags = str(r["flags"])
    if "figure_digitized" in flags:
        return "figure"
    if "abstract_only" in flags:
        return "abstract"
    return "fulltext"


def row_payload(r: dict[str, Any]) -> dict[str, Any]:
    flags = [f for f in str(r["flags"]).split(";") if f]
    return {
        "id": r["row_id"], "p": r["paper_id"], "doi": r["doi"], "t": r["paper_title"], "y": r["year"],
        "mat": r["matrix_polymer"], "mf": r["matrix_family"], "cur": r["curing_agent"],
        "fil": r["filler_material"], "fo": r["filler_material_original"], "fg": filler_group(r),
        "sh": r["filler_shape"], "al": r["filler_alignment"], "fn": r["functionalization"],
        "sz": _f(r["filler_mean_size_um"]), "pr": r["processing_method"],
        "v": _f(r["filler_loading_vol_pct"]), "w": _f(r["filler_loading_wt_pct"]),
        "lo": r["filler_loading_original_value"], "lu": r["filler_loading_original_unit"],
        "phi": _f(r["phi_vol_pct"]), "pb": r["phi_basis"],
        "k": float(r["k_composite_W_mK"]), "km": _f(r["k_matrix_effective"]), "kb": r["k_matrix_basis"],
        "en": _f(r["k_enhancement"]),
        "mc": r["method_class"], "mg": METHOD_FILTER.get(r["method_class"], "OTHER"), "mm": r["measurement_method"],
        "dr": r["direction_reported"], "de": r["direction_effective"], "db": r["direction_basis"],
        "kd": r["k_direction"], "T": _f(r["measurement_temperature_C"]),
        "vs": r["value_source"], "cf": r["confidence"], "pv": provenance_group(r),
        "sl": r["source_location"], "nt": r["notes"], "fl": flags,
    }


def model_curves(rk: float) -> dict[str, list[float]]:
    phi = np.linspace(0.005, 0.80, 160)
    props = filler_props("h-BN")
    kpar, kperp = float(props["k_in_plane"]), float(props["k_through_plane"])
    ceil = maxwell_limit_ratio(phi)
    n0 = nan1997(phi, KM_REF, kpar, kperp, p=0.05) / KM_REF
    nr = nan1997(phi, KM_REF, kpar, kperp, p=0.05, r_k=rk, a1_m=SIZE_REF_UM * 1e-6 / 2) / KM_REF
    clean = lambda a: [round(float(x), 5) if np.isfinite(x) and x > 0 else None for x in a]  # noqa: E731
    return {"phi": [round(float(x) * 100, 3) for x in phi], "ceiling": clean(ceil), "nan0": clean(n0),
            "nanr": clean(nr)}


def payload(lay: Layout) -> dict[str, Any]:
    records = load_records(lay).records
    fp = dataset_fingerprint(records)
    phys_path = lay.reports / "physics_summary.json"
    phys = json.loads(phys_path.read_text(encoding="utf-8")) if phys_path.exists() else {}
    check_fresh("reports/physics_summary.json", phys, fp, "argus physics")
    rk = float(phys["parameters"]["nan_R_K_m2K_W"]["median"])
    from ..release import citation_text

    meta = load_yaml(lay.data / "dataset.yaml") or {}
    rows = [row_payload(r) for r in enrich_records(records)]
    return {
        "meta": {"version": meta.get("version", ""), "released": meta.get("released", ""),
                 "license": meta.get("license", ""), "citation": citation_text(meta),
                 "fingerprint": fp["sha256"], "rows": fp["rows"], "papers": fp["papers"],
                 "generated": _dt.date.today().isoformat(), "rk_median": rk, "km_ref": KM_REF,
                 "size_ref_um": SIZE_REF_UM},
        "methods": {k: v.description for k, v in METHOD_CLASSES.items()},
        "curves": model_curves(rk),
        "rows": rows,
    }


def safe_json(obj: Any) -> str:
    """JSON that is safe inside <script type="application/json">."""
    s = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    return s.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026").replace("\u2028", "\\u2028") \
        .replace("\u2029", "\\u2029")


def _template(name: str) -> str:
    return resources.files("argus").joinpath(f"report/templates/{name}").read_text(encoding="utf-8")


def render(lay: Layout, out_dir: Path | None = None) -> dict[str, Path]:
    from jinja2 import Environment, StrictUndefined

    out_dir = out_dir or (lay.root / "docs" / "explorer")
    data = payload(lay)
    env = Environment(undefined=StrictUndefined, autoescape=True, keep_trailing_newline=True)
    ctx = {"meta": data["meta"]}
    head = env.from_string(_template("explorer_head.html.j2")).render(**ctx)
    body = env.from_string(_template("explorer_body.html.j2")).render(**ctx)
    script = _template("explorer.js")
    body = body.replace("<!--ARGUS_DATA-->", safe_json(data)).replace("/*ARGUS_SCRIPT*/", script)

    standalone = ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
                  "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1, viewport-fit=cover\">\n"
                  f"{head}</head>\n<body>\n{body}</body>\n</html>\n")
    fragment = head + body
    paths = {"standalone": out_dir / "index.html", "artifact": out_dir / "explorer.artifact.html"}
    atomic_write_text(paths["standalone"], standalone)
    atomic_write_text(paths["artifact"], fragment)
    return paths
