"""Phase 4 (v2): reproducible pixel-level digitization of figure-only k values.

Replaces the earlier visual estimates in phase4_figures_digitized.json, which
contained points not present in the figures (e.g. 3.6 um series at 10/20 vol%
in molecules21050670 Fig. 3, which starts at 30 vol%).

Method
  1. Axis calibration from detected tick marks (pixel positions hard-coded
     below were measured from the grey/black tick runs along each axis line).
  2. Per-series colour mask (Euclidean RGB distance to a reference colour).
  3. Binary opening with a disk to remove fitted curves and error bars
     (1-3 px wide), keeping filled markers (>= 9 px).
  4. Connected components -> centroid -> data coordinates.
Outputs: phase4_figures_digitized_v2.json and overlay PNGs in figures/ for
visual verification (detected centroids drawn as black crosses).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

W = Path(__file__).resolve().parent
FIG = W / "figures"

FIGURES = {
    "10.3390/polym11071156": {
        "file": "polymers-11-01156-g011.jpg",
        "caption": "Figure 11 Thermal conductivity of ETLBN and EJBN samples as a function of the BN content: "
                   "ETLBN2, blue circles; EJBN30, grey squares; ETLBN30, orange triangles; ETLBN180, purple diamonds.",
        # (pixel, value) pairs for two ticks per axis
        "x_cal": ((124.0, 0.0), (732.5, 50.0)),   # Vol% BN
        "y_cal": ((492.5, 0.0), (20.0, 4.5)),     # W/mK
        "series": {
            "ETLBN180 (purple diamonds)": (132, 45, 167),
            "ETLBN30 (orange triangles)": (250, 127, 39),
            "EJBN30 (grey squares)": (157, 157, 157),
            "ETLBN2 (blue circles)": (20, 140, 210),
        },
        "tol": 60,
        "open_radius": 3,
    },
    "10.3390/molecules21050670": {
        "file": "molecules-21-00670-g003.jpg",
        "caption": "Figure 3 Effects of surface treatment, h-BN particle size and filler content on thermal "
                   "conductivity of composites. (Series labelled in-plot: treated 10.6 um = filled green squares; "
                   "treated 3.6 um = filled blue circles; naked series are open markers and are not digitized.)",
        "x_cal": ((84.5, 0.0), (714.5, 100.0)),   # Filler Content (vol%)
        "y_cal": ((482.0, 0.0), (17.5, 8.0)),     # W/mK
        "series": {
            "treated 10.6um (filled green squares)": (2, 128, 2),
            "treated 3.6um (filled blue circles)": (2, 4, 249),
        },
        "tol": 90,
        "open_radius": 3,
        # Markers partly hidden under another series' marker: (series, pixel box r0, r1, c0, c1).
        # Centre = visible top edge + median half-height of that series' unoccluded markers.
        "occluded": [("treated 10.6um (filled green squares)", 355, 385, 260, 290)],
    },
}


def cal(p, c):
    (p0, v0), (p1, v1) = c
    return v0 + (p - p0) * (v1 - v0) / (p1 - p0)


def disk(r):
    y, x = np.ogrid[-r:r + 1, -r:r + 1]
    return x * x + y * y <= r * r


def point(spec, cx, cy, area):
    return {
        "x": round(float(cal(cx, spec["x_cal"])), 2),
        "k": round(float(cal(cy, spec["y_cal"])), 3),
        "px": [round(float(cx), 1), round(float(cy), 1)],
        "area_px": int(area),
    }


def digitize(spec):
    img = Image.open(FIG / spec["file"]).convert("RGB")
    a = np.asarray(img).astype(float)
    overlay = img.copy()
    dr = ImageDraw.Draw(overlay)
    out = {}
    for name, rgb in spec["series"].items():
        mask = np.sqrt(((a - np.array(rgb)) ** 2).sum(2)) < spec["tol"]
        mask = ndimage.binary_opening(mask, structure=disk(spec["open_radius"]))
        lab, n = ndimage.label(mask)
        pts, heights = [], []
        for i in range(1, n + 1):
            ys, xs = np.nonzero(lab == i)
            if len(ys) < 20:
                continue
            heights.append(ys.max() - ys.min() + 1)
            pts.append(point(spec, xs.mean(), ys.mean(), len(ys)))
        for s, r0, r1, c0, c1 in spec.get("occluded", []):
            if s != name:
                continue
            raw = np.sqrt(((a - np.array(rgb)) ** 2).sum(2)) < spec["tol"]
            ys, xs = np.nonzero(raw[r0:r1, c0:c1])
            half = (np.median(heights) - 1) / 2
            p = point(spec, c0 + xs.mean(), r0 + ys.min() + half, len(ys))
            p["occluded"] = ("partially hidden; centre = visible top edge + median half-height "
                             f"({half:.1f} px) of unoccluded markers in this series")
            pts.append(p)
        for p in pts:
            cx, cy = p["px"]
            dr.line([(cx - 6, cy), (cx + 6, cy)], fill=(0, 0, 0), width=1)
            dr.line([(cx, cy - 6), (cx, cy + 6)], fill=(0, 0, 0), width=1)
        out[name] = sorted(pts, key=lambda p: p["x"])
    overlay.save(FIG / ("overlay_" + spec["file"].replace(".jpg", ".png")))
    return out


def main():
    result = {}
    for doi, spec in FIGURES.items():
        px_x = abs(spec["x_cal"][1][0] - spec["x_cal"][0][0]) / abs(spec["x_cal"][1][1] - spec["x_cal"][0][1])
        px_y = abs(spec["y_cal"][1][0] - spec["y_cal"][0][0]) / abs(spec["y_cal"][1][1] - spec["y_cal"][0][1])
        result[doi] = {
            "source": spec["file"],
            "caption": spec["caption"],
            "method": "pixel digitization: tick-calibrated axes, colour mask, disk opening, component centroid "
                      "(work/phase4_digitize_v2.py)",
            "resolution": {"x_units_per_px": round(1 / px_x, 4), "k_W_mK_per_px": round(1 / px_y, 4)},
            "series": digitize(spec),
        }
    (W / "phase4_figures_digitized_v2.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    for doi, r in result.items():
        print(doi, r["resolution"])
        for s, pts in r["series"].items():
            print("  ", s, [(p["x"], p["k"], p["area_px"]) for p in pts])


if __name__ == "__main__":
    main()
