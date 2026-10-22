import math

import pytest
from conftest import good_measurement, make_record

from argus.enrich import DERIVED_NAMES, density_check, enrich_records
from argus.validate import validate_records
from argus.vocab import (
    METHOD_CLASSES,
    classify_filler,
    classify_matrix,
    classify_method,
    direction_hint,
    filler_props,
    matrix_prefilled,
    normalize_direction,
)


@pytest.mark.parametrize("text,cls,basis", [
    ("Laser flash (Netzsch LFA447); K = Cp·ρ·α", "LFA", "named"),
    ("Laser flash (TC-3000H-NC, Sinku-Riko), density by water displacement", "LFA", "named"),
    ("TC 3000 Series thermal conductivity apparatus (Xi'an Xiaxi, transient hot-wire)", "HOT_WIRE", "named"),
    ("TC-3000 thermal conductivity instrument", "HOT_WIRE", "instrument"),
    ("Hot disk (this-work table row); laser flash for some literature rows", "TPS", "named"),
    ("LFA (NETZSCH LFA 467) at 25 C; IR camera validation", "LFA", "named"),
    ("Hot Disk TPS2500 (transient plate heat source, ISO 22007-2)", "TPS", "named"),
    ("DZDR-S thermal conductivity tester (transient plane source), vertical direction", "TPS", "named"),
    ("Quick thermal conductivity meter (Xiangyi)", "TPS", "instrument"),
    ("Transient hot bridge (Linseis THB-100)", "THB", "named"),
    ("Steady-state heat flow, DRL-III (ASTM D5470-2006)", "SS_D5470", "named"),
    ("Plane heat flow method (DRL-III, Xiangtan)", "SS_D5470", "named"),
    ("Thermal conductivity tester DTC-300 (TA Instruments)", "SS_GHFM", "named"),
    ("Steady-state method, 25 C", "SS_UNSPECIFIED", "generic"),
    ("Laser thermal diffusivity, ULVAC Laser-PIT-M2 (in-plane)", "PERIODIC", "named"),
    ("Periodic heating-temperature, Thermowave Analyzer TA3 (Bethel)", "PERIODIC", "named"),
    ("hot-plate + thermo-camera setup", "IR_THERMO", "named"),
    ("Not stated in abstract", "UNSPECIFIED", "none"),
    ("", "UNSPECIFIED", "none"),
])
def test_method_classes(text, cls, basis):
    m = classify_method(text)
    assert (m.method_class, m.basis) == (cls, basis)


def test_every_dataset_method_string_classifies_and_named_ones_dominate(repo_layout):
    from argus.records import load_records

    rows = enrich_records(load_records(repo_layout).records)
    assert all(r["method_class"] in METHOD_CLASSES for r in rows)
    # Methods that are stated must not silently fall through to UNSPECIFIED.
    stated = [r for r in rows if any(w in r["measurement_method"].lower()
                                     for w in ("flash", "hot disk", "hot bridge", "hot-wire", "d5470"))]
    assert all(r["method_class"] != "UNSPECIFIED" for r in stated)


@pytest.mark.parametrize("text,label", [
    ("unknown", "unknown"), ("", "unknown"), ("through-plane (vertical alignment)", "through-plane"),
    ("out-of-plane", "through-plane"), ("vertical", "through-plane"), ("through-thickness", "through-plane"),
    ("sheet plane (in-plane", "in-plane"), ("in-plane", "in-plane"), ("isotropic", "isotropic"),
])
def test_direction_normalization(text, label):
    assert normalize_direction(text) == label


def test_direction_hint_requires_a_single_direction():
    assert direction_hint("LFA (Netzsch LFA 447) perpendicular to film plane") == "through-plane"
    assert direction_hint("Laser flash (LFA467 Netzsch), through-plane and in-plane") == "unknown"
    assert direction_hint("Hot Disk TPS 2500S") == "unknown"


def test_filler_and_matrix_classes():
    assert classify_filler("h-BN").family == "BN"
    hy = classify_filler("Al2O3/BN hybrid")
    assert hy.is_hybrid and hy.contains_bn and hy.components == ("Al2O3", "BN")
    assert classify_filler("none").family == "none"
    assert classify_matrix("Cresol novolac epoxy (CNE200EL)") == "epoxy"
    assert classify_matrix("Silicone gel (SG)") == "silicone"
    assert classify_matrix("Polyimide (PI)") == "polyimide"
    assert matrix_prefilled("Commercial bicomponent epoxy resin containing Al2O3 and SiO2 fillers (already loaded resin)")
    assert filler_props("BN") == filler_props("h-BN")  # alias


def _enrich_one(**over):
    return enrich_records([make_record(measurements=[good_measurement(**over)])])[0]


def test_enriched_row_has_all_derived_columns_and_keeps_originals():
    r = _enrich_one(measurement_method="Laser flash (LFA 467)", k_direction="unknown")
    assert set(DERIVED_NAMES) <= set(r)
    assert r["k_direction"] == "unknown"  # original untouched
    assert (r["direction_effective"], r["direction_basis"]) == ("through-plane", "method-default")


def test_wt_converted_to_vol_with_basis():
    r = _enrich_one(filler_loading_wt_pct=30.0, filler_loading_vol_pct=None)
    assert r["phi_basis"] == "converted-from-wt"
    assert math.isclose(r["phi_vol_pct"], 30 / 2.16 / (30 / 2.16 + 70 / 1.17) * 100, rel_tol=1e-3)
    assert r["rho_filler_used"] == 2.16 and r["rho_matrix_used"] == 1.17


def test_reported_vol_wins_and_hybrids_are_not_converted():
    assert _enrich_one(filler_loading_vol_pct=20.0)["phi_basis"] == "reported"
    r = _enrich_one(filler_material="Al2O3/BN hybrid", filler_loading_vol_pct=None)
    assert r["phi_basis"] == "unavailable-hybrid" and r["phi_vol_pct"] == ""


def test_bias_flags():
    tps = _enrich_one(measurement_method="Hot Disk TPS 2500S", k_direction="unknown")
    assert "mixed_direction_anisotropic" in tps["flags"] and tps["direction_effective"] == "mixed"
    aln = _enrich_one(filler_material="AlN", measurement_method="Hot Disk TPS 2500S")
    assert "mixed_direction_anisotropic" not in aln["flags"]  # isotropic particles
    d5470 = _enrich_one(measurement_method="Steady-state heat flow, DRL-III (ASTM D5470)")
    assert "contact_resistance_included" in d5470["flags"]
    lfa = _enrich_one(measurement_method="LFA (Netzsch NanoFlash LFA 467); Cp DSC, rho densimeter")
    assert "lfa_cp_rho_unreported" not in lfa["flags"] and lfa["k_rel_uncertainty"] == 0.05


def test_matrix_k_default_is_labelled():
    r = _enrich_one(k_matrix_W_mK=None)
    assert (r["k_matrix_effective"], r["k_matrix_basis"]) == (0.2, "reference-default")
    assert math.isclose(r["k_enhancement"], 1.2 / 0.2, rel_tol=1e-6)


def test_loading_basis_warning_catches_designation_stored_as_wt():
    # 30 "wt%" with 12.9 vol% printed: the D2 defect pattern found in P094
    bad = make_record(measurements=[good_measurement(filler_loading_wt_pct=30.0, filler_loading_vol_pct=12.9)])
    assert [i.rule for i in validate_records([bad])] == ["loading_basis_consistent"]
    ok = make_record(measurements=[good_measurement(filler_loading_wt_pct=20.2, filler_loading_vol_pct=12.9)])
    assert validate_records([ok]) == []


def test_reference_densities_agree_with_rows_reporting_both(repo_layout):
    from argus.records import load_records

    dc = density_check(enrich_records(load_records(repo_layout).records))
    assert dc["n_rows"] >= 30
    assert dc["max_abs_diff_vol_pct"] <= 5.0
    assert dc["median_abs_diff_vol_pct"] <= 2.5
