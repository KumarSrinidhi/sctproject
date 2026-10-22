"""Linear mixed model with a random intercept per group, fitted by REML.

    y = X beta + u_g + e,   u_g ~ N(0, tau^2),   e ~ N(0, sigma^2)

Small and dependency-free (numpy/scipy). With lambda = tau^2/sigma^2 the
covariance of group g is sigma^2 (I + lambda J), whose inverse is
(I - c_g J)/sigma^2 with c_g = lambda / (1 + n_g lambda). beta and sigma^2 are
profiled out and the REML criterion is maximised over log(lambda).

Degrees of freedom follow the between/within rule: a covariate that is constant
within every group (e.g. the measurement method, fixed per paper) is tested
against the number of groups, not the number of rows. This matters here: most
papers use one technique, so method effects rest on between-paper contrasts.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from scipy import stats
from scipy.optimize import minimize_scalar


@dataclass
class LMMResult:
    names: list[str]
    beta: np.ndarray
    se: np.ndarray
    df: np.ndarray
    ci_low: np.ndarray
    ci_high: np.ndarray
    sigma2: float
    tau2: float
    n: int
    groups: int
    between: list[bool] = field(default_factory=list)
    reml_loglik: float = float("nan")

    @property
    def icc(self) -> float:
        """Share of the residual variance that sits between groups."""
        tot = self.tau2 + self.sigma2
        return self.tau2 / tot if tot > 0 else 0.0

    def coef(self, name: str) -> dict[str, float]:
        i = self.names.index(name)
        return {"beta": float(self.beta[i]), "se": float(self.se[i]), "df": float(self.df[i]),
                "ci_low": float(self.ci_low[i]), "ci_high": float(self.ci_high[i]),
                "between_group": bool(self.between[i])}


def _group_slices(groups: np.ndarray) -> list[np.ndarray]:
    _, inv = np.unique(groups, return_inverse=True)
    return [np.flatnonzero(inv == g) for g in range(inv.max() + 1)]


def _profile(lam: float, X: np.ndarray, y: np.ndarray, idx: list[np.ndarray]) -> tuple[float, np.ndarray, float, np.ndarray]:
    """REML criterion (to maximise), beta, sigma^2 and A = X' W X at a given lambda."""
    N, p = X.shape
    A = np.zeros((p, p))
    b = np.zeros(p)
    logdet_v = 0.0
    for ix in idx:
        Xg, yg, ng = X[ix], y[ix], len(ix)
        c = lam / (1 + ng * lam)
        sx, sy = Xg.sum(0), yg.sum()
        A += Xg.T @ Xg - c * np.outer(sx, sx)
        b += Xg.T @ yg - c * sx * sy
        logdet_v += math.log1p(ng * lam)
    beta = np.linalg.solve(A, b)
    Q = 0.0
    for ix in idx:
        r = y[ix] - X[ix] @ beta
        c = lam / (1 + len(ix) * lam)
        Q += r @ r - c * r.sum() ** 2
    sigma2 = Q / (N - p)
    sign, logdet_a = np.linalg.slogdet(A)
    ll = -0.5 * ((N - p) * math.log(sigma2) + logdet_v + logdet_a + (N - p))
    return ll, beta, sigma2, A


def fit_lmm(y: np.ndarray, X: np.ndarray, groups: np.ndarray, names: list[str], level: float = 0.95) -> LMMResult:
    y, X, groups = np.asarray(y, float), np.asarray(X, float), np.asarray(groups)
    N, p = X.shape
    if N <= p:
        raise ValueError("more parameters than observations")
    if np.linalg.matrix_rank(X) < p:
        raise ValueError("design matrix is rank deficient (collinear covariates)")
    idx = _group_slices(groups)
    G = len(idx)

    res = minimize_scalar(lambda t: -_profile(math.exp(t), X, y, idx)[0], bounds=(-14.0, 9.0), method="bounded",
                          options={"xatol": 1e-7})
    cand = [(-res.fun, math.exp(res.x)), (_profile(0.0, X, y, idx)[0], 0.0)]
    ll, lam = max(cand)
    ll, beta, sigma2, A = _profile(lam, X, y, idx)
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(A)))

    # between/within degrees of freedom
    between = []
    for j in range(p):
        col = X[:, j]
        between.append(all(np.ptp(col[ix]) == 0 for ix in idx))
    p_b = sum(between)
    p_w = p - p_b
    df_b = max(1, G - p_b)
    df_w = max(1, N - G - p_w)
    df = np.array([df_b if bt else df_w for bt in between], float)
    tq = stats.t.ppf(0.5 + level / 2, df)
    return LMMResult(names=list(names), beta=beta, se=se, df=df, ci_low=beta - tq * se, ci_high=beta + tq * se,
                     sigma2=float(sigma2), tau2=float(lam * sigma2), n=N, groups=G, between=between,
                     reml_loglik=float(ll))


def fit_ols(y: np.ndarray, X: np.ndarray, names: list[str], level: float = 0.95) -> dict[str, dict[str, float]]:
    """Ordinary least squares ignoring the grouping (for contrast only)."""
    y, X = np.asarray(y, float), np.asarray(X, float)
    N, p = X.shape
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    r = y - X @ beta
    s2 = r @ r / (N - p)
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    tq = stats.t.ppf(0.5 + level / 2, N - p)
    return {n: {"beta": float(b), "se": float(s), "ci_low": float(b - tq * s), "ci_high": float(b + tq * s)}
            for n, b, s in zip(names, beta, se)}
