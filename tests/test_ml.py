"""Phase 5 ML: features, leakage-safe validation, baselines and intervals."""
import math

import numpy as np
import pytest

pytest.importorskip("sklearn")
pytest.importorskip("xgboost")

from argus.ml.benchmark import (  # noqa: E402
    Config,
    group_conformal,
    group_kfold_splits,
    lopo_splits,
    metrics,
    oof_predictions,
    random_kfold_splits,
    run_benchmark,
)
from argus.ml.features import (  # noqa: E402
    NAMES,
    Dataset,
    build_dataset,
    feature_row,
    is_aligned,
    is_treated,
    shape_group,
)
from argus.ml.models import GroupRidge, PhysicsCalibrated, fit_model, zoo  # noqa: E402


@pytest.fixture(scope="module")
def real_ds(request):
    from conftest import REPO

    from argus.enrich import enrich_records
    from argus.paths import Layout
    from argus.records import load_records

    return build_dataset(enrich_records(load_records(Layout(REPO)).records))


# ---------------------------------------------------------------- features

def test_real_features_are_finite_and_complete(real_ds):
    assert real_ds.X.shape == (len(real_ds.y), len(NAMES))
    assert np.all(np.isfinite(real_ds.X)) and np.all(np.isfinite(real_ds.y))
    assert len(real_ds.y) >= 150 and real_ds.n_papers >= 50
    assert all(not r["filler_material"].lower().endswith("hybrid") for r in real_ds.rows)


def test_feature_helpers():
    assert shape_group("platelet", "") == "platelet"
    assert shape_group("nanosheet network", "") == "network"
    assert shape_group("other", "continuous 3D skeleton (porous ceramic preform)") == "network"
    assert shape_group("Sphere", "") == "particle"
    assert not is_treated("None (as received)") and not is_treated("")
    assert is_treated("GPTMS silane surface treatment")
    assert is_aligned("vertically aligned") and not is_aligned("random") and not is_aligned("")


def _template(**over):
    r = {"phi_vol_pct": 20.0, "k_matrix_effective": 0.2, "filler_base": "h-BN", "filler_shape": "platelet",
         "filler_alignment": "", "filler_mean_size_um": "", "method_class": "LFA", "flags": "", "year": 2021,
         "functionalization": "", "direction_reported": "unknown", "matrix_family": "epoxy",
         "k_matrix_basis": "reported"}
    r.update(over)
    return r


def test_physics_feature_rises_with_loading():
    i = NAMES.index("phys_nan")
    vals = [feature_row(_template(phi_vol_pct=p))[i] for p in (5, 10, 20, 40)]
    assert vals == sorted(vals) and vals[0] > 0


# ---------------------------------------------------------------- splits

def test_grouped_splits_never_share_a_paper(real_ds):
    for splits in (lopo_splits(real_ds), group_kfold_splits(real_ds, 1)):
        for tr, te in splits:
            assert not set(real_ds.groups[tr]) & set(real_ds.groups[te])


def test_random_splits_do_share_papers(real_ds):
    shared = [bool(set(real_ds.groups[tr]) & set(real_ds.groups[te])) for tr, te in random_kfold_splits(real_ds, 1)]
    assert all(shared)  # this is exactly the leak the benchmark reports


# ---------------------------------------------------------------- models

def test_physics_calibration_recovers_line():
    rng = np.random.default_rng(0)
    X = rng.uniform(0, 1, size=(60, 3))
    y = 0.2 + 0.7 * X[:, 1]
    m = PhysicsCalibrated(col=1).fit(X, y)
    assert np.allclose(m.coef_, [0.2, 0.7])


def test_group_ridge_selects_alpha_with_groups():
    rng = np.random.default_rng(1)
    X = rng.normal(size=(80, 4))
    y = X @ np.array([1.0, -0.5, 0.0, 0.2]) + rng.normal(0, 0.1, 80)
    g = np.repeat(np.arange(20), 4)
    m = fit_model(GroupRidge(), X, y, g)
    assert m.alpha_ in m.alphas and np.corrcoef(m.predict(X), y)[0, 1] > 0.95


def test_xgboost_is_monotone_in_loading(real_ds):
    model = fit_model(zoo(quick=True)["xgboost"][1](real_ds.names), real_ds.X, real_ds.y, real_ds.groups)
    for base in ("h-BN", "BNNS", "AlN"):
        grid = np.array([feature_row(_template(filler_base=base, phi_vol_pct=p)) for p in np.linspace(1, 60, 30)])
        pred = model.predict(grid)
        assert np.all(np.diff(pred) >= -1e-9), base


# ---------------------------------------------------------------- leakage and intervals

def _synthetic_ds(papers=30, rows=6, seed=3):
    """Strong paper effects + a paper-identifying feature: random CV can memorise the
    paper, grouped CV cannot."""
    rng = np.random.default_rng(seed)
    X, y, g = [], [], []
    yc = NAMES.index("log_size")  # any free column can carry a paper id
    for p in range(papers):
        u = rng.normal(0, 0.4)
        for _ in range(rows):
            x = np.zeros(len(NAMES))
            x[NAMES.index("phi")] = phi = rng.uniform(0.05, 0.4)
            x[NAMES.index("phys_nan")] = 2 * phi
            x[yc] = p  # identifies the paper
            X.append(x)
            y.append(0.2 + 2 * phi + u + rng.normal(0, 0.05))
            g.append(f"P{p:03d}")
    return Dataset(X=np.array(X), y=np.array(y), groups=np.array(g), names=list(NAMES),
                   rows=[{"year": 2020, "filler_base": "h-BN"}] * (papers * rows))


def test_random_cv_overstates_accuracy_when_papers_differ():
    # gradient boosting memorises the paper-identifying feature: across 5 seeds the
    # leaky/grouped MAE ratio was 0.35-0.53, so 0.7 leaves a wide margin
    ds = _synthetic_ds()
    factory = zoo(quick=True)["xgboost"][1]
    grouped = metrics(ds.y, oof_predictions(factory, ds, group_kfold_splits(ds, 0)))["mae_log10"]
    leaky = metrics(ds.y, oof_predictions(factory, ds, random_kfold_splits(ds, 0)))["mae_log10"]
    assert leaky < 0.7 * grouped


def test_group_conformal_is_calibrated_on_exchangeable_papers():
    ds = _synthetic_ds(papers=60, rows=5, seed=9)
    rng = np.random.default_rng(4)
    pred = ds.y + rng.normal(0, 0.1, len(ds.y))
    c90 = group_conformal(ds, pred, 0.10)
    assert abs(c90["row_coverage"] - 0.90) < 0.05
    c68 = group_conformal(ds, pred, 0.32)
    assert abs(c68["row_coverage"] - 0.68) < 0.07


def test_metrics_basics():
    y = np.array([0.0, 1.0, 2.0])
    m = metrics(y, y + np.array([0.1, -0.1, 0.4]))
    assert m["n"] == 3 and math.isclose(m["mae_log10"], 0.2, abs_tol=1e-4)
    assert m["within_factor_2"] == round(2 / 3, 3)


def test_benchmark_runs_on_real_data(real_ds):
    res = run_benchmark(real_ds, Config.fast(), models=["median", "physics", "knn"])
    M = res["models"]
    assert M["physics"]["lopo"]["mae_log10"] < M["median"]["lopo"]["mae_log10"]
    assert M["knn"]["lopo"]["n"] == len(real_ds.y)
    assert 0.8 < M["physics"]["conformal_90"]["row_coverage"] <= 1.0
    assert res["best_model"] is None and "acceptance" not in res  # baselines only
