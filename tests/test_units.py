import math

import pytest

from argus.io import read_jsonl
from argus.units import k_unit_factor, normalize_k, phr_to_wt, vol_to_wt, wt_to_vol


@pytest.mark.parametrize("unit", [
    "W/mK", "W m-1 K-1", "W m−1 K−1", "Wm–1 K–1", "W∙m−1∙K−1", "W/(m·K)", "W·m−1·K−1", "W/m·K",
    "W/m K", "W (m−1 K−1)", "W/(m K)", "W/mk", "Wm−1K−1", "W/m∙K", "W (m-1 K-1)",
    "W/K.m (= W/(m K))", "Wm-1 K-1", "W/(m*K)", "W/(m∙K)", "W/m-K", "W/m°C", "W·m^-1·K^-1",
])
def test_si_spellings_are_unity(unit):
    assert k_unit_factor(unit) == 1.0


@pytest.mark.parametrize("unit,factor", [
    ("mW/(m·K)", 1e-3), ("kW/mK", 1e3), ("μW/(m·K)", 1e-6), ("µW/mK", 1e-6),
    ("W/cmK", 100.0), ("W/(cm·K)", 100.0), ("W/mmK", 1000.0),
    ("cal/(cm·s·K)", 418.4), ("cal cm-1 s-1 K-1", 418.4),
    ("BTU/(h·ft·°F)", 1.730735), ("Btu·in/(h·ft²·°F)", 0.1442279),
])
def test_prefixed_and_legacy_units(unit, factor):
    assert math.isclose(k_unit_factor(unit), factor)


@pytest.mark.parametrize("unit", ["", "W/m2K", "W/K", "m2/s", "W/mm", "mm2/s", "J/(kg K)", "S/m"])
def test_non_conductivity_units_rejected(unit):
    # audit D4: the legacy fallback accepted anything with w, m and k in it
    assert k_unit_factor(unit) is None
    assert normalize_k(1.0, unit) is None


def test_every_unit_in_the_dataset_is_recognised(repo_layout):
    rows = read_jsonl(repo_layout.compiled_jsonl)
    unknown = {r["k_original_unit"] for r in rows if k_unit_factor(r["k_original_unit"]) is None}
    assert not unknown


def test_wt_vol_roundtrip():
    for w in (0.0, 5.0, 30.0, 60.0, 95.0, 100.0):
        v = wt_to_vol(w, 2.28, 1.2)
        assert math.isclose(vol_to_wt(v, 2.28, 1.2), w, abs_tol=1e-9)


def test_wt_to_vol_known_value():
    # 30 wt% h-BN (2.28) in epoxy (1.20): (0.3/2.28) / (0.3/2.28 + 0.7/1.2) = 18.40 vol%
    assert math.isclose(wt_to_vol(30.0, 2.28, 1.20), 18.4049, rel_tol=1e-4)


def test_wt_to_vol_range_checked():
    with pytest.raises(ValueError):
        wt_to_vol(120.0, 2.28, 1.2)


def test_phr():
    assert math.isclose(phr_to_wt(5.0), 4.7619, rel_tol=1e-4)  # matches row 'phr (4.76 wt%)'
