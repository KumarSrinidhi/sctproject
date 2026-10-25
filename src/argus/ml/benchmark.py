"""Benchmark: can composition, processing and method predict k for an unseen paper?

Validation schemes (every learned step happens inside the training fold):

  lopo          leave-one-paper-out: the honest headline number
  group5        5-fold by paper, repeated with different paper shuffles
  random5       5-fold over rows, repeated; leaks paper identity across the
                split and is reported ONLY to show the size of that leak
  time          train on papers up to 2021, test on 2022+
  filler_out    hold out one filler family entirely (extrapolation)

Prediction intervals: group-conformal. For each held-out paper the interval
half-width is the (1 - alpha) quantile of the absolute leave-one-paper-out
residuals of all OTHER papers.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass
from typing import Any, Iterable, Iterator

import numpy as np
from sklearn.model_selection import GroupKFold, KFold, LeaveOneGroupOut

from .features import COLUMNS, FILLER_GROUP, Dataset, is_aligned, shape_group
from .models import BASELINES, SEED, fit_model, zoo

FACTOR2 = math.log10(2.0)
Split = tuple[np.ndarray, np.ndarray]
# Groups that carry overlapping information (the physics feature is a function of
# loading; method implies a default direction) are also removed together.
ABLATION_COMBOS = (("loading", "physics"), ("direction", "method"))


# --------------------------------------------------------------------------- splits

def lopo_splits(ds: Dataset) -> Iterator[Split]:
    yield from LeaveOneGroupOut().split(ds.X, ds.y, ds.groups)


def group_kfold_splits(ds: Dataset, seed: int, k: int = 5) -> Iterator[Split]:
    yield from GroupKFold(n_splits=k, shuffle=True, random_state=seed).split(ds.X, ds.y, ds.groups)


def random_kfold_splits(ds: Dataset, seed: int, k: int = 5) -> Iterator[Split]:
    yield from KFold(n_splits=k, shuffle=True, random_state=seed).split(ds.X)


def time_split(ds: Dataset, last_train_year: int = 2021) -> list[Split]:
    years = np.array([int(r["year"]) for r in ds.rows])
    tr, te = np.flatnonzero(years <= last_train_year), np.flatnonzero(years > last_train_year)
    return [(tr, te)] if len(tr) and len(te) else []


def filler_out_splits(ds: Dataset, min_rows: int = 15) -> dict[str, Split]:
    fam = np.array([FILLER_GROUP[r["filler_base"]] for r in ds.rows])
    out = {}
    for f in sorted(set(fam)):
        te = np.flatnonzero(fam == f)
        if len(te) >= min_rows:
            out[f] = (np.flatnonzero(fam != f), te)
    return out


# --------------------------------------------------------------------------- core

def oof_predictions(factory, ds: Dataset, splits: Iterable[Split], cols: list[int] | None = None) -> np.ndarray:
    """Out-of-fold predictions; rows never in a test fold stay NaN."""
    cols = cols if cols is not None else list(range(ds.X.shape[1]))
    names = [ds.names[i] for i in cols]
    X = ds.X[:, cols]
    pred = np.full(len(ds.y), np.nan)
    for tr, te in splits:
        model = fit_model(factory(names), X[tr], ds.y[tr], ds.groups[tr])
        pred[te] = model.predict(X[te])
    return pred


def metrics(y: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    m = ~np.isnan(pred)
    y, p = y[m], pred[m]
    err = p - y
    ss_res = float(np.sum(err ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    mae = float(np.mean(np.abs(err)))
    return {
        "n": int(m.sum()),
        "mae_log10": round(mae, 4),
        "mae_factor": round(10 ** mae, 3),
        "rmse_log10": round(math.sqrt(ss_res / len(y)), 4),
        "r2": round(1 - ss_res / ss_tot, 3) if ss_tot > 0 else None,
        "within_factor_2": round(float(np.mean(np.abs(err) <= FACTOR2)), 3),
        "bias_log10": round(float(np.mean(err)), 4),
    }


def group_conformal(ds: Dataset, pred: np.ndarray, alpha: float) -> dict[str, Any]:
    """Coverage of leave-one-paper-out intervals built from OTHER papers' residuals."""
    res = np.abs(pred - ds.y)
    covered, widths, per_paper = [], [], []
    for p in sorted(set(ds.groups.tolist())):
        mine = ds.groups == p
        others = res[~mine & ~np.isnan(res)]
        n = len(others)
        level = min(1.0, (1 - alpha) * (n + 1) / n)
        q = float(np.quantile(others, level, method="higher"))
        hit = res[mine] <= q
        covered.extend(hit.tolist())
        widths.extend([q] * int(mine.sum()))
        per_paper.append(float(hit.mean()))
    return {
        "nominal": round(1 - alpha, 3),
        "row_coverage": round(float(np.mean(covered)), 3),
        "paper_coverage_mean": round(float(np.mean(per_paper)), 3),
        "half_width_log10_median": round(float(np.median(widths)), 3),
        "interval_factor_median": round(10 ** float(np.median(widths)), 2),
    }


@dataclass
class Config:
    quick: bool = False
    repeats: int = 5
    ablation_repeats: int = 5

    @classmethod
    def fast(cls) -> "Config":
        return cls(quick=True, repeats=2, ablation_repeats=2)


def _runs(factory, ds: Dataset, kind: str, repeats: int, cols: list[int] | None = None) -> list[dict[str, float]]:
    """One metrics dict per repeat; repeat r always uses the same split (seed SEED + r),
    so runs with different feature sets are paired."""
    runs = []
    for r in range(repeats):
        splits = (group_kfold_splits if kind == "group5" else random_kfold_splits)(ds, SEED + r)
        runs.append(metrics(ds.y, oof_predictions(factory, ds, splits, cols)))
    return runs


def _repeated(factory, ds: Dataset, kind: str, repeats: int, cols: list[int] | None = None) -> dict[str, Any]:
    runs = _runs(factory, ds, kind, repeats, cols)
    keys = ("mae_log10", "rmse_log10", "r2", "within_factor_2")
    out = {k: round(statistics.mean(x[k] for x in runs), 4) for k in keys}
    out["mae_log10_sd"] = round(statistics.pstdev(x["mae_log10"] for x in runs), 4)
    out["mae_factor"] = round(10 ** out["mae_log10"], 3)
    out["repeats"] = repeats
    return out


def run_benchmark(ds: Dataset, cfg: Config | None = None, models: list[str] | None = None) -> dict[str, Any]:
    cfg = cfg or Config()
    z = zoo(quick=cfg.quick)
    names = models or list(z)
    out: dict[str, Any] = {
        "data": {"rows": len(ds.y), "papers": ds.n_papers, "features": len(ds.names),
                 "target": "log10(k / k_matrix_effective)", "target_sd": round(float(np.std(ds.y)), 4),
                 "feature_groups": sorted(set(COLUMNS.values()))},
        "models": {}, "lopo_predictions": {},
    }
    fo = filler_out_splits(ds)
    ts = time_split(ds)
    for name in names:
        desc, factory = z[name]
        lopo = oof_predictions(factory, ds, lopo_splits(ds))
        out["lopo_predictions"][name] = lopo
        entry = {
            "description": desc, "baseline": name in BASELINES,
            "lopo": metrics(ds.y, lopo),
            "group5": _repeated(factory, ds, "group5", cfg.repeats),
            "random5": _repeated(factory, ds, "random5", cfg.repeats),
            "time_split": metrics(ds.y, oof_predictions(factory, ds, ts)) if ts else None,
            "filler_out": {f: metrics(ds.y, oof_predictions(factory, ds, [sp])) for f, sp in fo.items()},
            "conformal_90": group_conformal(ds, lopo, 0.10),
            "conformal_68": group_conformal(ds, lopo, 0.32),
        }
        entry["leakage_gap_mae"] = round(entry["group5"]["mae_log10"] - entry["random5"]["mae_log10"], 4)
        out["models"][name] = entry

    ranked = sorted(names, key=lambda n: out["models"][n]["lopo"]["mae_log10"])
    best_base = min((n for n in names if n in BASELINES), key=lambda n: out["models"][n]["lopo"]["mae_log10"],
                    default=None)
    best_model = next((n for n in ranked if n not in BASELINES), None)
    out["ranking_lopo_mae"] = ranked
    out["best_baseline"] = best_base
    out["best_model"] = best_model
    if best_base and best_model:
        b, m = out["models"][best_base]["lopo"], out["models"][best_model]["lopo"]
        out["acceptance"] = {
            "criterion": "best learned model beats the best baseline (physics, kNN, median) on leave-one-paper-out MAE",
            "best_baseline_mae": b["mae_log10"], "best_model_mae": m["mae_log10"],
            "improvement_log10": round(b["mae_log10"] - m["mae_log10"], 4),
            "passed": m["mae_log10"] < b["mae_log10"],
        }
    # time split: what differs between the older and newer papers
    if ts:
        def mix(idx: np.ndarray) -> dict[str, float]:
            rows = [ds.rows[i] for i in idx]
            share = lambda pred: round(sum(map(pred, rows)) / len(rows), 3)  # noqa: E731
            return {"rows": int(len(idx)), "papers": len({r["paper_id"] for r in rows}),
                    "share_BNNS": share(lambda r: r["filler_base"] == "BNNS"),
                    "share_aligned": share(lambda r: is_aligned(r["filler_alignment"])),
                    "share_network": share(lambda r: shape_group(r["filler_shape"], r["filler_alignment"]) == "network"),
                    "median_target_log10": round(float(np.median(ds.y[idx])), 3)}
        out["data"]["time_split"] = {"train_years": "<= 2021", "test_years": ">= 2022",
                                     "train": mix(ts[0][0]), "test": mix(ts[0][1])}
    out["data"]["filler_out"] = {f: int(len(sp[1])) for f, sp in fo.items()}
    return out


def ablation(ds: Dataset, model: str, cfg: Config | None = None) -> dict[str, Any]:
    """Grouped-CV MAE when each feature group is removed (positive delta = the group helps)."""
    cfg = cfg or Config()
    z = zoo(quick=cfg.quick)
    _, factory = z[model]
    full = [m["mae_log10"] for m in _runs(factory, ds, "group5", cfg.ablation_repeats)]
    rows = []
    singles = [(g,) for g in sorted(set(COLUMNS.values()))]
    for combo in singles + list(ABLATION_COMBOS):
        g = " + ".join(combo)
        cols = ds.columns(drop=set(combo))
        if model in ("physics", "gp_residual", "ensemble") and "physics" in combo:
            continue
        without = [m["mae_log10"] for m in _runs(factory, ds, "group5", cfg.ablation_repeats, cols)]
        deltas = [w - f for w, f in zip(without, full)]  # paired: same split in each repeat
        sd = statistics.stdev(deltas) if len(deltas) > 1 else None
        rows.append({"group": g, "mae_without": round(statistics.mean(without), 4),
                     "delta_mae": round(statistics.mean(deltas), 4),
                     "delta_sd": round(sd, 4) if sd is not None else None,
                     "clear": bool(sd is not None and statistics.mean(deltas) > 2 * sd)})
    rows.sort(key=lambda r: -r["delta_mae"])
    return {"model": model, "scheme": f"group5 x{cfg.ablation_repeats} (paired splits)",
            "repeats": cfg.ablation_repeats, "mae_all_features": round(statistics.mean(full), 4), "groups": rows}
