"""Model zoo: two baselines that any useful model must beat, plus four learners.

All estimators follow the scikit-learn fit/predict protocol. Estimators that
tune themselves accept `groups` in fit() and tune with an inner split that
also keeps papers intact (no paper on both sides of an inner split).
"""
from __future__ import annotations

import inspect
from typing import Callable

import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin, TransformerMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, ConstantKernel, WhiteKernel
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SEED = 20261022
LOADING_MONOTONE = ("phi", "phi2", "phys_nan", "phys_maxwell_ceiling")


class Columns(BaseEstimator, TransformerMixin):
    """Select columns by index (stateless)."""

    def __init__(self, idx: tuple[int, ...] = ()):
        self.idx = idx

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        return np.asarray(X)[:, list(self.idx)]


class Median(BaseEstimator, RegressorMixin):
    """Baseline 0: predict the training median enhancement."""

    def fit(self, X, y):
        self.value_ = float(np.median(y))
        return self

    def predict(self, X):
        return np.full(len(X), self.value_)


class PhysicsCalibrated(BaseEstimator, RegressorMixin):
    """Baseline 1: y = a + b * log10(k_Nan/km), a and b fitted on the training fold.
    Nan 1997 with random orientation and perfect interfaces supplies the shape
    of the loading curve; the calibration absorbs interface and contact losses."""

    def __init__(self, col: int = 0):
        self.col = col

    def fit(self, X, y):
        x = np.asarray(X)[:, self.col]
        A = np.column_stack([np.ones_like(x), x])
        self.coef_ = np.linalg.lstsq(A, y, rcond=None)[0]
        return self

    def predict(self, X):
        return self.coef_[0] + self.coef_[1] * np.asarray(X)[:, self.col]


class GroupRidge(BaseEstimator, RegressorMixin):
    """Standardised ridge regression; alpha chosen by grouped inner CV."""

    def __init__(self, alphas: tuple[float, ...] = tuple(np.logspace(-2, 3, 16)), inner_splits: int = 4):
        self.alphas = alphas
        self.inner_splits = inner_splits

    def _make(self, alpha):
        return make_pipeline(StandardScaler(), Ridge(alpha=alpha))

    def fit(self, X, y, groups=None):
        X, y = np.asarray(X), np.asarray(y)
        alpha = float(np.median(self.alphas))
        if groups is not None and len(set(groups)) >= self.inner_splits:
            cv = GroupKFold(n_splits=self.inner_splits)
            scores = []
            for a in self.alphas:
                err = 0.0
                for tr, te in cv.split(X, y, groups):
                    m = self._make(a).fit(X[tr], y[tr])
                    err += float(np.abs(m.predict(X[te]) - y[te]).sum())
                scores.append(err)
            alpha = float(self.alphas[int(np.argmin(scores))])
        self.alpha_ = alpha
        self.model_ = self._make(alpha).fit(X, y)
        return self

    def predict(self, X):
        return self.model_.predict(X)


class ResidualGP(BaseEstimator, RegressorMixin):
    """Physics-informed residual learning: calibrated Nan baseline + a Gaussian
    process on its residuals (research report: EMT as mean function)."""

    def __init__(self, col: int = 0):
        self.col = col

    def fit(self, X, y):
        X, y = np.asarray(X), np.asarray(y)
        self.base_ = PhysicsCalibrated(self.col).fit(X, y)
        r = y - self.base_.predict(X)
        self.scaler_ = StandardScaler().fit(X)
        kernel = (ConstantKernel(0.05, (1e-4, 10.0)) * RBF(length_scale=5.0, length_scale_bounds=(0.3, 300.0))
                  + WhiteKernel(0.02, (1e-5, 1.0)))
        self.gp_ = GaussianProcessRegressor(kernel=kernel, normalize_y=False, random_state=SEED,
                                            n_restarts_optimizer=1).fit(self.scaler_.transform(X), r)
        return self

    def predict(self, X):
        X = np.asarray(X)
        return self.base_.predict(X) + self.gp_.predict(self.scaler_.transform(X))


def _xgb(names: list[str], quick: bool):
    from xgboost import XGBRegressor

    # every feature that rises with loading is constrained, so predictions cannot fall as loading rises
    mono = tuple(1 if n in LOADING_MONOTONE else 0 for n in names)
    return XGBRegressor(n_estimators=150 if quick else 400, max_depth=3, learning_rate=0.05, subsample=0.8,
                        colsample_bytree=0.8, min_child_weight=3, reg_lambda=1.0, monotone_constraints=mono,
                        random_state=SEED, n_jobs=1, verbosity=0)


ModelFactory = Callable[[list[str]], BaseEstimator]


def zoo(quick: bool = False) -> dict[str, tuple[str, ModelFactory]]:
    """name -> (description, factory(feature_names) -> estimator)."""

    def idx(names: list[str], wanted: list[str]) -> tuple[int, ...]:
        return tuple(names.index(w) for w in wanted if w in names)

    return {
        "median": ("Baseline: training median (no information)", lambda names: Median()),
        "physics": ("Baseline: Nan 1997 random platelets, calibrated a + b*log enhancement",
                    lambda names: PhysicsCalibrated(col=names.index("phys_nan"))),
        "knn": ("Baseline: 5 nearest neighbours on loading + filler type",
                lambda names: make_pipeline(Columns(idx(names, ["phi", "f_BNNS", "f_AlN", "f_oxide"])),
                                            StandardScaler(), KNeighborsRegressor(n_neighbors=5, weights="distance"))),
        "ridge": ("Ridge regression on all features (alpha by grouped inner CV)", lambda names: GroupRidge()),
        "gp_residual": ("Calibrated physics + Gaussian process on residuals",
                        lambda names: ResidualGP(col=names.index("phys_nan"))),
        "xgboost": ("Gradient boosting, constrained to be non-decreasing in loading", lambda names: _xgb(names, quick)),
        "random_forest": ("Random forest (500 trees, min leaf 3)",
                          lambda names: RandomForestRegressor(n_estimators=150 if quick else 500, min_samples_leaf=3,
                                                              max_features=0.5, random_state=SEED, n_jobs=-1)),
    }


BASELINES = ("median", "physics", "knn")


def fit_model(model: BaseEstimator, X: np.ndarray, y: np.ndarray, groups: np.ndarray) -> BaseEstimator:
    """Fit, passing groups to estimators that accept them."""
    if "groups" in inspect.signature(model.fit).parameters:
        return model.fit(X, y, groups=groups)
    return model.fit(X, y)
