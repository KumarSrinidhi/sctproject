"""Phase 4 bias analysis: the mixed model, pair finders and uncertainty budget."""
import math

import numpy as np
import pytest

from argus.analysis.bias import (
    SPECS,
    analyze,
    direction_pairs,
    method_pairs,
    pooled_model,
    render_markdown,
    uncertainty_rows,
)
from argus.analysis.lmm import fit_lmm, fit_ols


# ---------------------------------------------------------------- mixed model

def _synthetic(G=40, n=5, beta=(0.5, 1.2, 0.3), tau=0.25, sigma=0.08, seed=7):
    rng = np.random.default_rng(seed)
    X, y, g = [], [], []
    for j in range(G):
        z = float(j % 2)  # between-group covariate (like the method used by a paper)
        u = rng.normal(0, tau)
        for _ in range(n):
            x = rng.uniform(0, 0.5)  # within-group covariate (like loading)
            X.append([1.0, x, z])
            y.append(beta[0] + beta[1] * x + beta[2] * z + u + rng.normal(0, sigma))
            g.append(f"P{j:03d}")
    return np.array(y), np.array(X), np.array(g)


def test_lmm_recovers_known_parameters():
    y, X, g = _synthetic()
    fit = fit_lmm(y, X, g, ["intercept", "x", "z"])
    truth = (0.5, 1.2, 0.3)
    for i, b in enumerate(truth):
        assert abs(fit.beta[i] - b) < 3 * fit.se[i], (i, fit.beta[i], fit.se[i])
    assert 0.15 < math.sqrt(fit.tau2) < 0.35
    assert 0.065 < math.sqrt(fit.sigma2) < 0.095
    assert fit.between == [True, False, True]
    assert fit.df[2] == 40 - 2  # between-group df: groups minus between-group columns
    assert fit.ci_low[2] < 0.3 < fit.ci_high[2]


def test_between_group_ci_is_wider_than_naive_ols():
    y, X, g = _synthetic()
    fit = fit_lmm(y, X, g, ["intercept", "x", "z"])
    ols = fit_ols(y, X, ["intercept", "x", "z"])
    assert (fit.ci_high[2] - fit.ci_low[2]) > 1.5 * (ols["z"]["ci_high"] - ols["z"]["ci_low"])


def test_lmm_without_group_effect_matches_ols():
    y, X, g = _synthetic(tau=0.0, seed=3)
    fit = fit_lmm(y, X, g, ["intercept", "x", "z"])
    ols = fit_ols(y, X, ["intercept", "x", "z"])
    assert fit.icc < 0.05
    assert abs(fit.beta[1] - ols["x"]["beta"]) < 0.02


def test_group_algebra_matches_dense_reml():
    """The per-group shortcuts in _profile must equal brute-force dense algebra."""
    from argus.analysis.lmm import _group_slices, _profile

    y, X, g = _synthetic(G=6, n=4, seed=5)
    g = np.array(list(g[:-3]) + ["P099"] * 3)  # unequal group sizes
    idx = _group_slices(g)
    Z = np.zeros((len(y), len(idx)))
    for j, ix in enumerate(idx):
        Z[ix, j] = 1.0
    N, p = X.shape
    for lam in (0.0, 0.3, 5.0):
        H = np.eye(N) + lam * Z @ Z.T
        Hi = np.linalg.inv(H)
        A = X.T @ Hi @ X
        beta = np.linalg.solve(A, X.T @ Hi @ y)
        r = y - X @ beta
        s2 = (r @ Hi @ r) / (N - p)
        ll = -0.5 * ((N - p) * math.log(s2) + np.linalg.slogdet(H)[1] + np.linalg.slogdet(A)[1] + (N - p))
        ll2, beta2, s2b, _ = _profile(lam, X, y, idx)
        assert math.isclose(ll, ll2, rel_tol=1e-9) and np.allclose(beta, beta2) and math.isclose(s2, s2b)


def test_collinear_design_is_rejected():
    y, X, g = _synthetic()
    X = np.column_stack([X, X[:, 2]])
    with pytest.raises(ValueError):
        fit_lmm(y, X, g, ["intercept", "x", "z", "z_copy"])


# ---------------------------------------------------------------- enriched-row helpers

def row(**over):
    r = {"row_id": "x-001", "paper_id": "P001", "doi": "10.1/p1", "matrix_polymer": "Epoxy", "curing_agent": "",
         "filler_material": "h-BN", "filler_shape": "platelet", "filler_mean_size_um": "", "functionalization": "",
         "filler_alignment": "", "processing_method": "", "measurement_temperature_C": "",
         "filler_loading_vol_pct": 20.0, "filler_loading_wt_pct": "", "filler_loading_original_value": 20.0,
         "phi_vol_pct": 20.0, "k_composite_W_mK": 1.0, "k_matrix_effective": 0.2, "k_matrix_basis": "reported",
         "filler_base": "h-BN", "is_hybrid": False, "direction_reported": "unknown", "method_class": "LFA",
         "flags": "", "value_source": "table", "notes": "", "k_rel_uncertainty": 0.05}
    r.update(over)
    return r


def test_direction_pair_found_and_ratio():
    rows = [row(direction_reported="in-plane", k_composite_W_mK=3.0),
            row(row_id="x-002", direction_reported="through-plane", k_composite_W_mK=0.5),
            row(row_id="x-003", filler_loading_vol_pct=30.0, direction_reported="through-plane")]  # other loading
    pairs = direction_pairs(rows)
    assert len(pairs) == 1 and pairs[0].ratio == 6.0


def test_method_pair_needs_same_sample_and_direction():
    rows = [row(method_class="LFA", k_composite_W_mK=1.0),
            row(row_id="x-002", method_class="TPS", k_composite_W_mK=1.4),
            row(row_id="x-003", method_class="UNSPECIFIED")]  # unnamed methods are not compared
    pairs = method_pairs(rows)
    assert len(pairs) == 1 and math.isclose(pairs[0].k_b / pairs[0].k_a, 1.4)


def test_pooled_model_recovers_a_method_offset():
    rng = np.random.default_rng(11)
    rows = []
    true_factor = 1.5
    for j in range(40):
        method = "THB" if j % 2 else "LFA"
        u = rng.normal(0, 0.2)
        for i, phi in enumerate((5.0, 10.0, 20.0, 30.0)):
            y = 0.1 + 3 * phi / 100 + (math.log10(true_factor) if method == "THB" else 0) + u + rng.normal(0, 0.05)
            rows.append(row(row_id=f"r{j}-{i}", paper_id=f"P{j:03d}", doi=f"10.1/{j}", phi_vol_pct=phi,
                            filler_loading_vol_pct=phi, k_composite_W_mK=0.2 * 10 ** y, method_class=method))
    m = pooled_model(rows, SPECS[0])
    e = m["effects"]["method:MIXED"]
    assert e["ci95"][0] < true_factor < e["ci95"][1]
    assert abs(e["factor"] - true_factor) / true_factor < 0.2
    assert e["between_paper_contrast"] and e["papers"] == 20


def test_uncertainty_budget_adds_digitization_in_quadrature():
    rows = [row(), row(row_id="x-002", value_source="figure", k_composite_W_mK=0.5,
                       notes="Figure-only value; Axis resolution ~0.01 W/mK per px.")]
    u = {x["row_id"]: x for x in uncertainty_rows(rows)}
    assert u["x-001"]["rel_sigma_digitization"] == 0.0
    assert math.isclose(u["x-002"]["rel_sigma_digitization"], 0.02)
    assert math.isclose(u["x-002"]["rel_sigma_total"], round(math.hypot(0.05, 0.02), 4))


def test_real_dataset_analysis_runs(repo_layout):
    from argus.enrich import enrich_records
    from argus.records import load_records

    res = analyze(enrich_records(load_records(repo_layout).records))
    assert res["anisotropy"]["n_pairs"] >= 1
    main = res["pooled_models"]["main"]
    assert main["n"] > 100 and "method:MIXED" in main["effects"]
    md = render_markdown(res)
    assert "## 1. Same-sample evidence" in md and "## 5. Caveats" in md
