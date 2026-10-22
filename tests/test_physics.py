"""Effective-medium models: limits, identities and independent reference numbers.

The 'research' numbers were computed independently during the 2026-10-22
research pass (docs/reports/BN epoxy thermal conductivity research.md, physics
section) from the published equations; matching them guards against sign and
convention slips (p = t/D, semi-axis Kapitza convention, the '2 - phi' sign).
"""
import math

import numpy as np
import pytest

from argus.physics.emt import (
    agari_uno,
    bruggeman_dem,
    bruggeman_symmetric,
    coated_conductivities,
    depolarization,
    foygel,
    geometric_mean,
    hashin_shtrikman,
    hasselman_johnson,
    lewis_nielsen,
    maxwell_garnett,
    maxwell_limit_ratio,
    nan1997,
    parallel,
    series,
)

KM, KF = 0.2, 400.0
PHI = np.linspace(0, 0.6, 13)


def close(a, b, tol=1e-9):
    return np.allclose(np.asarray(a, float), np.asarray(b, float), rtol=tol, atol=tol)


# ---------------------------------------------------------------- limits

@pytest.mark.parametrize("model", [
    lambda f: maxwell_garnett(f, KM, KF),
    lambda f: hasselman_johnson(f, KM, KF, 1e-6, 1e-8),
    lambda f: bruggeman_symmetric(f, KM, KF),
    lambda f: bruggeman_dem(f, KM, KF),
    lambda f: bruggeman_dem(f, KM, KF, r_k=1e-8, radius_m=1e-6),
    lambda f: lewis_nielsen(f, KM, KF, 1.5, 0.637),
    lambda f: agari_uno(f, KM, KF, 1.0, 0.8),
    lambda f: geometric_mean(f, KM, KF),
    lambda f: nan1997(f, KM, 400, 5, p=0.05, r_k=1e-7, a1_m=2.5e-6),
    lambda f: parallel(f, KM, KF),
    lambda f: series(f, KM, KF),
])
def test_zero_loading_gives_matrix(model):
    assert close(model(0.0), KM)


@pytest.mark.parametrize("model", [
    lambda f: maxwell_garnett(f, KM, KF), lambda f: bruggeman_symmetric(f, KM, KF),
    lambda f: bruggeman_dem(f, KM, KF), lambda f: geometric_mean(f, KM, KF),
    lambda f: parallel(f, KM, KF), lambda f: series(f, KM, KF),
])
def test_full_loading_gives_filler(model):
    assert close(model(1.0), KF, 1e-7)


def test_percent_is_rejected():
    with pytest.raises(ValueError):
        maxwell_garnett(30.0, KM, KF)


# ---------------------------------------------------------------- bounds

def test_bound_ordering_and_models_inside_hs():
    lo, hi = hashin_shtrikman(PHI, KM, KF)
    s, p = series(PHI, KM, KF), parallel(PHI, KM, KF)
    assert np.all(s <= lo + 1e-12) and np.all(lo <= hi + 1e-12) and np.all(hi <= p + 1e-12)
    for k in (bruggeman_symmetric(PHI, KM, KF), bruggeman_dem(PHI, KM, KF)):
        assert np.all(k >= lo - 1e-9) and np.all(k <= hi + 1e-9)


def test_maxwell_is_hs_lower_bound():
    assert close(maxwell_garnett(PHI, KM, KF), hashin_shtrikman(PHI, KM, KF)[0])


def test_maxwell_limit_ratio_is_the_kf_to_infinity_limit():
    assert close(maxwell_garnett(0.3, KM, 1e12) / KM, maxwell_limit_ratio(0.3), 1e-6)


# ---------------------------------------------------------------- identities

def test_hasselman_johnson_without_resistance_is_maxwell():
    assert close(hasselman_johnson(PHI, KM, KF, 1e-6, 0.0), maxwell_garnett(PHI, KM, KF))


def test_hasselman_johnson_is_maxwell_with_effective_filler():
    a, rk = 2e-6, 5e-8
    kf_eff = KF / (1 + KF * rk / a)
    assert close(hasselman_johnson(PHI, KM, KF, a, rk), maxwell_garnett(PHI, KM, kf_eff))


def test_nan_sphere_reduces_to_maxwell_and_hj():
    assert close(nan1997(PHI, KM, KF, p=1.0), maxwell_garnett(PHI, KM, KF))
    a, rk = 3e-6, 2e-8
    assert close(nan1997(PHI, KM, KF, p=1.0, r_k=rk, a1_m=a), hasselman_johnson(PHI, KM, KF, a, rk))


def test_nan_random_orientation_is_isotropic():
    k33 = nan1997(PHI, KM, 400, 5, p=0.05, cos2=1 / 3, axis="33")
    k11 = nan1997(PHI, KM, 400, 5, p=0.05, cos2=1 / 3, axis="11")
    assert close(k33, k11)


def test_nan_orientation_ordering_for_hbn():
    # platelets standing up (cos2=0) conduct along their basal planes: highest k33
    up = nan1997(0.3, KM, 400, 5, p=0.05, cos2=0.0)
    rnd = nan1997(0.3, KM, 400, 5, p=0.05, cos2=1 / 3)
    flat = nan1997(0.3, KM, 400, 5, p=0.05, cos2=1.0)
    assert up > rnd > flat


def test_agari_uno_c1_c2_one_is_geometric_mean():
    assert close(agari_uno(PHI, KM, KF, 1.0, 1.0), geometric_mean(PHI, KM, KF))


def test_every_dem_reduces_to_dem_and_decreases_with_resistance():
    assert close(bruggeman_dem(PHI, KM, KF, r_k=1e-14, radius_m=1e-6), bruggeman_dem(PHI, KM, KF), 1e-5)
    k = [float(bruggeman_dem(0.4, KM, KF, r_k=rk, radius_m=1e-6)) for rk in (0, 1e-8, 1e-7, 1e-6)]
    assert k == sorted(k, reverse=True)


def test_foygel_is_flat_below_threshold():
    assert close(foygel([0.0, 0.1, 0.2], KM, 7.0, 0.23, 0.35), KM)
    assert foygel(0.4, KM, 7.0, 0.23, 0.35) > KM


# ---------------------------------------------------------------- geometry

def test_depolarization_limits_and_sum():
    for p in (1e-4, 0.05, 0.5, 0.9999, 1.0, 1.0001, 2.0, 50.0):
        L11, L33 = depolarization(p)
        assert math.isclose(2 * L11 + L33, 1.0)
    assert math.isclose(depolarization(1.0)[1], 1 / 3)
    assert depolarization(1e-5)[1] > 0.9999  # thin disc
    assert math.isclose(depolarization(1e5)[0], 0.5, abs_tol=1e-4)  # long needle


def test_depolarization_continuous_through_the_sphere():
    # mixes the closed forms (|p-1| >= 1e-4) and the series expansion (|p-1| < 1e-4):
    # L33 must fall smoothly and monotonically through p = 1 with slope -4/15
    ps = [0.9997, 0.99985, 0.99995, 1.0, 1.00005, 1.00015, 1.0003]
    L33 = [depolarization(p)[1] for p in ps]
    assert all(a > b for a, b in zip(L33, L33[1:]))
    slopes = [(b - a) / (q - p) for (p, a), (q, b) in zip(zip(ps, L33), zip(ps[1:], L33[1:]))]
    assert all(abs(s + 4 / 15) < 1e-3 for s in slopes)


def test_kapitza_slab_and_needle_limits():
    # thin slab: K33c -> kp / (1 + r_k kp / a3) (two interfaces in series with thickness 2 a3)
    a1, p, rk, kp = 5e-6, 1e-5, 1e-7, 5.0
    _, k33 = coated_conductivities(KM, 400, kp, p, rk, a1)
    assert math.isclose(k33, kp / (1 + rk * kp / (p * a1)), rel_tol=1e-3)
    # long needle, transverse: K11c -> kp / (1 + r_k kp / a1)
    k11, _ = coated_conductivities(KM, 30.0, 30.0, 1e5, rk, 1e-6)
    assert math.isclose(k11, 30.0 / (1 + rk * 30.0 / 1e-6), rel_tol=1e-3)


# ---------------------------------------------------------------- research cross-checks

def test_research_coated_platelet_values():
    # D = 5 um, t = 250 nm (p = 0.05), h-BN 400 / 5, R_K = 1e-7
    k11, k33 = coated_conductivities(KM, 400, 5, 0.05, 1e-7, 2.5e-6)
    assert round(k11, 1) == 28.6 and round(k33, 2) == 0.99


@pytest.mark.parametrize("rk,expected", [(0.0, [0.60, 1.74, 3.75]), (1e-7, [0.54, 1.43, 2.82])])
def test_research_nan_random_platelets(rk, expected):
    k = nan1997([0.1, 0.3, 0.5], KM, 400, 5, p=0.05, r_k=rk, a1_m=2.5e-6)
    assert np.allclose(k, expected, atol=0.006)


def test_research_vertical_platelets():
    k = nan1997([0.1, 0.3, 0.5], KM, 400, 5, p=0.05, r_k=1e-8, a1_m=2.5e-6, cos2=0.0)
    assert np.allclose(k, [0.78, 2.42, 5.30], atol=0.006)


def test_research_lewis_nielsen_kargar_fit():
    # Kargar et al. 2018 h-BN/epoxy fit: A = 31, apparent kf = 16, phi_m = 0.52
    assert np.allclose(lewis_nielsen([0.1, 0.3, 0.45], KM, 16, 31, 0.52), [0.70, 2.27, 5.16], atol=0.006)


def test_research_maxwell_and_bruggeman():
    assert np.allclose(maxwell_garnett([0.1, 0.3, 0.45], KM, KF), [0.27, 0.46, 0.69], atol=0.006)
    assert np.allclose(bruggeman_symmetric([0.1, 0.3, 0.45], KM, KF), [0.29, 1.84, 70.6], atol=0.06)
