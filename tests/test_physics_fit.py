"""Model fitting: recover known parameters from synthetic series."""
import math

import numpy as np

from argus.physics.emt import lewis_nielsen, maxwell_garnett, nan1997
from argus.physics.fit import SeriesFit, build_series, fit_series, maxwell_ceiling_share, summarize

KM = 0.2
PHI = [0.05, 0.10, 0.20, 0.30]


def _series(k, filler="h-BN", shape="platelet", size_key=""):
    key = ("10.1/x", "Epoxy", "", filler, shape, size_key, "", "", "", "unknown", "LFA", "")
    return SeriesFit(key=key, paper_id="P001", doi="10.1/x", filler=filler, shape_class=shape,
                     direction="through-plane", method_class="LFA", phi=list(PHI), k=list(k),
                     km=KM, km_basis="reported", kf_ref=(2 * 400 + 4.8) / 3)


def test_recovers_lewis_nielsen_A():
    k = lewis_nielsen(np.array(PHI), KM, (2 * 400 + 4.8) / 3, 12.0, 0.52)
    f = fit_series(_series(k)).fits["ln_A"]
    assert math.isclose(f["A"], 12.0, rel_tol=1e-3) and f["rmse_log10"] < 1e-5


def test_recovers_nan_interface_resistance():
    rk = 3e-7
    k = nan1997(np.array(PHI), KM, 400, 4.8, p=0.05, r_k=rk, a1_m=5e-6)  # 10 um platelets
    f = fit_series(_series(k, size_key=10.0)).fits["nan_rk"]
    assert math.isclose(f["R_K_m2K_W"], rk, rel_tol=1e-2) and f["rmse_log10"] < 1e-4
    assert f["convention"].startswith("semi-axis")


def test_agari_is_exact_on_log_linear_data():
    k = KM * 10 ** (2.0 * np.array(PHI))
    f = fit_series(_series(k)).fits["agari"]
    assert f["rmse_log10"] < 1e-9 and math.isclose(f["C1"], 1.0, rel_tol=1e-6)


def test_maxwell_cannot_reach_platelet_data():
    # random h-BN platelets far exceed what any sphere model can give
    k = nan1997(np.array(PHI), KM, 400, 4.8, p=0.05)
    f = fit_series(_series(k)).fits["maxwell_kf"]
    assert f["at_bound"] and f["rmse_log10"] > 0.1
    assert maxwell_garnett(0.3, KM, 1e9) < k[-1]


def _row(phi, k, **over):
    r = {"doi": "10.1/x", "paper_id": "P001", "matrix_polymer": "Epoxy", "curing_agent": "", "filler_material": "h-BN",
         "filler_shape": "platelet", "filler_mean_size_um": "", "functionalization": "", "filler_alignment": "",
         "processing_method": "", "k_direction": "unknown", "measurement_method": "LFA",
         "measurement_temperature_C": "", "phi_vol_pct": phi, "k_composite_W_mK": k, "k_matrix_W_mK": 0.2,
         "k_matrix_basis": "reported", "k_matrix_effective": 0.2, "direction_effective": "through-plane",
         "method_class": "LFA"}
    r.update(over)
    return r


def test_series_grouping_needs_three_loadings_and_single_filler():
    rows = [_row(5, 0.3), _row(10, 0.5), _row(20, 0.9),
            _row(10, 0.6, processing_method="hot pressed"),  # different condition: own group
            _row(10, 0.7, filler_material="Al2O3/BN hybrid")]  # hybrids skipped
    series = build_series(rows)
    assert len(series) == 1 and series[0].phi == [0.05, 0.10, 0.20]


def test_ceiling_share_and_summary_shape():
    rows = [_row(10, 0.6), _row(10, 0.25)]  # 0.6/0.2 = 3 > 1.33 ; 0.25/0.2 = 1.25 < 1.33
    assert maxwell_ceiling_share(rows) == {"rows_with_phi": 2, "above_maxwell_ceiling": 1, "share": 0.5}
    s = summarize([fit_series(_series(lewis_nielsen(np.array(PHI), KM, 268.3, 12.0, 0.52)))], rows)
    assert s["series"] == 1 and s["free_parameters"]["agari"] == 2
