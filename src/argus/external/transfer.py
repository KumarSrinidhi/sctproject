"""Train on one dataset, test on another: the out-of-distribution check that
leave-one-paper-out inside ARGUS cannot give.

Intervals use the training set's own leave-one-paper-out residuals (the same
group-conformal recipe as the benchmark), so coverage on the external set says
whether the stated uncertainty survives a change of curator and literature.

The external test sets are small in papers (EVF: 14), so every MAE comes with a
cluster bootstrap over test papers, and model comparisons are paired (same
resampled papers for both models).
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any, Callable

import numpy as np

from ..ml.benchmark import lopo_splits, metrics, oof_predictions
from ..ml.features import FILLER_GROUP, Dataset
from ..ml.models import SEED, fit_model, zoo

DEFAULT_MODELS = ("median", "physics", "knn", "ridge", "gp_residual", "xgboost", "random_forest", "ensemble")
N_BOOT = 2000


def subset(ds: Dataset, mask: np.ndarray) -> Dataset:
    idx = np.flatnonzero(mask)
    return Dataset(X=ds.X[idx], y=ds.y[idx], groups=ds.groups[idx], names=ds.names,
                   rows=[ds.rows[i] for i in idx])


def in_domain(train: Dataset, row: dict[str, Any]) -> bool:
    """Filler and matrix family both represented in the training set."""
    fillers = {r["filler_base"] for r in train.rows}
    matrices = {r["matrix_family"] for r in train.rows}
    return row["filler_base"] in fillers and row["matrix_family"] in matrices


def _paper_mae(ds: Dataset, pred: np.ndarray) -> float:
    per = defaultdict(list)
    for g, e in zip(ds.groups.tolist(), np.abs(pred - ds.y).tolist()):
        per[g].append(e)
    return round(float(np.mean([np.mean(v) for v in per.values()])), 4)


MIN_BOOT_PAPERS = 3  # with fewer papers a paper-level interval is meaningless


def cluster_bootstrap(groups: np.ndarray, stat: Callable[[np.ndarray], float], n: int = N_BOOT,
                      seed: int = SEED) -> tuple[float, float] | None:
    """95 % percentile interval of `stat(row_index)` when whole papers are resampled;
    None when there are fewer than MIN_BOOT_PAPERS papers."""
    rng = np.random.default_rng(seed)
    papers = sorted(set(groups.tolist()))
    if len(papers) < MIN_BOOT_PAPERS:
        return None
    idx_of = {p: np.flatnonzero(groups == p) for p in papers}
    vals = []
    for _ in range(n):
        pick = rng.choice(len(papers), size=len(papers), replace=True)
        idx = np.concatenate([idx_of[papers[i]] for i in pick])
        vals.append(stat(idx))
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return round(float(lo), 4), round(float(hi), 4)


def _breakdown(ds: Dataset, pred: np.ndarray, key) -> dict[str, Any]:
    out = {}
    labels = np.array([key(r) for r in ds.rows])
    for lab in sorted(set(labels.tolist())):
        m = labels == lab
        if m.sum() >= 3:
            out[lab] = {**metrics(ds.y[m], pred[m]), "papers": len(set(ds.groups[m].tolist()))}
    return out


def transfer(train: Dataset, test: Dataset, models: tuple[str, ...] = DEFAULT_MODELS, quick: bool = False,
             alpha: float = 0.10, reference: str = "physics", n_boot: int = N_BOOT) -> dict[str, Any]:
    """Fit each model on all of `train`, predict `test`.

    Interval half-width: the (1 - alpha) quantile of the model's leave-one-paper-out
    residuals on `train`. `reference` is the model every other is compared with
    (paired paper bootstrap of the MAE difference; negative = better than reference).
    """
    z = zoo(quick=quick)
    out: dict[str, Any] = {
        "train": {"rows": int(len(train.y)), "papers": train.n_papers},
        "test": {"rows": int(len(test.y)), "papers": test.n_papers},
        "alpha": alpha, "quick": quick, "reference": reference, "models": {}, "predictions": {},
    }
    if not len(test.y):
        return out
    dom = np.array([in_domain(train, r) for r in test.rows])
    out["test"]["in_domain_rows"] = int(dom.sum())
    out["test"]["in_domain_papers"] = len(set(test.groups[dom].tolist()))
    abs_err: dict[str, np.ndarray] = {}
    for name in models:
        _, factory = z[name]
        model = fit_model(factory(list(train.names)), train.X, train.y, train.groups)
        pred = model.predict(test.X)
        lopo = oof_predictions(factory, train, lopo_splits(train))
        res = np.abs(lopo - train.y)
        res = res[~np.isnan(res)]
        n = len(res)
        q = float(np.quantile(res, min(1.0, (1 - alpha) * (n + 1) / n), method="higher"))
        err = np.abs(pred - test.y)
        abs_err[name] = err
        hit = err <= q
        entry = {
            "test": metrics(test.y, pred),
            "test_mae_ci95": cluster_bootstrap(test.groups, lambda i, e=err: float(e[i].mean()), n_boot),
            "paper_mean_mae": _paper_mae(test, pred),
            "train_lopo_mae": metrics(train.y, lopo)["mae_log10"],
            "interval": {"nominal": round(1 - alpha, 3), "half_width_log10": round(q, 3),
                         "factor": round(10 ** q, 2), "coverage": round(float(hit.mean()), 3)},
            "in_domain": metrics(test.y[dom], pred[dom]) if dom.any() else None,
            "out_of_domain": metrics(test.y[~dom], pred[~dom]) if (~dom).any() else None,
            "by_filler": _breakdown(test, pred, lambda r: r["filler_base"]),
            "by_filler_group": _breakdown(test, pred, lambda r: FILLER_GROUP.get(r["filler_base"], "other")),
            "by_matrix": _breakdown(test, pred, lambda r: r["matrix_family"]),
        }
        out["models"][name] = entry
        out["predictions"][name] = pred
    if reference in abs_err:
        ref = abs_err[reference]
        for name, err in abs_err.items():
            if name == reference:
                continue
            d = err - ref
            ci = cluster_bootstrap(test.groups, lambda i, d=d: float(d[i].mean()), n_boot)
            out["models"][name]["vs_reference"] = {"mae_diff": round(float(d.mean()), 4), "ci95": ci,
                                                   "clear": bool(ci and (ci[1] < 0 or ci[0] > 0))}
    out["ranking_test_mae"] = sorted(out["models"], key=lambda m: out["models"][m]["test"]["mae_log10"])
    return out


def pooled(train: Dataset, ext: Dataset, models: tuple[str, ...] = ("physics", "ridge", "gp_residual", "xgboost",
                                                                    "random_forest", "ensemble"),
           quick: bool = False, n_boot: int = N_BOOT) -> dict[str, Any]:
    """Would adding the external rows to training help? Leave-one-paper-out over
    the pooled papers, scored separately on each side and compared (paired by
    paper) with training on `train` alone."""
    z = zoo(quick=quick)
    P = Dataset(X=np.vstack([train.X, ext.X]), y=np.concatenate([train.y, ext.y]),
                groups=np.concatenate([train.groups, ext.groups]), names=train.names, rows=train.rows + ext.rows)
    is_train = np.arange(len(P.y)) < len(train.y)
    out: dict[str, Any] = {"rows": int(len(P.y)), "papers": P.n_papers, "models": {}}
    for name in models:
        _, factory = z[name]
        p = oof_predictions(factory, P, lopo_splits(P))
        alone = oof_predictions(factory, train, lopo_splits(train))
        transfer_pred = fit_model(factory(list(train.names)), train.X, train.y, train.groups).predict(ext.X)
        d_train = np.abs(p[is_train] - train.y) - np.abs(alone - train.y)
        d_ext = np.abs(p[~is_train] - ext.y) - np.abs(transfer_pred - ext.y)
        out["models"][name] = {
            "train_rows": {"alone_lopo": metrics(train.y, alone)["mae_log10"],
                           "pooled_lopo": metrics(train.y, p[is_train])["mae_log10"],
                           "diff": round(float(d_train.mean()), 4),
                           "ci95": cluster_bootstrap(train.groups, lambda i, d=d_train: float(d[i].mean()), n_boot)},
            "external_rows": {"transfer": metrics(ext.y, transfer_pred)["mae_log10"],
                              "pooled_lopo": metrics(ext.y, p[~is_train])["mae_log10"],
                              "diff": round(float(d_ext.mean()), 4),
                              "ci95": cluster_bootstrap(ext.groups, lambda i, d=d_ext: float(d[i].mean()), n_boot)},
        }
    return out
