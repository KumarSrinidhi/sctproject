from conftest import good_measurement, make_record, rid

from argus.schema import Waiver
from argus.validate import errors, validate_records


def rules(issues):
    return {i.rule for i in issues}


def test_clean_record_has_no_issues():
    assert validate_records([make_record()]) == []


def test_missing_k_blocks():
    rec = make_record(measurements=[good_measurement(k_composite_W_mK=None)])
    assert "k_present_positive" in rules(errors(validate_records([rec])))


def test_rejected_row_is_reported_not_silently_kept():
    # audit D1: a failing row must surface as an error (the build then refuses to write)
    rec = make_record(measurements=[good_measurement(source_location="")])
    errs = errors(validate_records([rec]))
    assert [e.rule for e in errs] == ["source_location_present"]


def test_unknown_unit_blocks():
    rec = make_record(measurements=[good_measurement(k_original_unit="W/m2K")])
    assert "k_unit_known" in rules(validate_records([rec]))


def test_normalization_must_match():
    # 1200 mW/(m K) is 1.2 W/(m K): consistent. 1.2 mW/(m K) is not.
    ok = make_record(measurements=[good_measurement(k_original_value=1200.0, k_original_unit="mW/(m·K)")])
    bad = make_record(measurements=[good_measurement(k_original_value=1.2, k_original_unit="mW/(m·K)")])
    assert validate_records([ok]) == []
    assert "k_normalized_consistent" in rules(validate_records([bad]))


def test_loading_required_and_waivable():
    m = good_measurement(filler_loading_wt_pct=None)
    assert "loading_present" in rules(validate_records([make_record(measurements=[m])]))
    m.waivers = [Waiver(rule="loading_present", reason="Source gives a sample designation only")]
    assert validate_records([make_record(measurements=[m])]) == []


def test_loading_range():
    rec = make_record(measurements=[good_measurement(filler_loading_vol_pct=140.0)])
    assert "loading_range" in rules(validate_records([rec]))


def test_figure_and_abstract_values_cannot_be_high():
    fig = good_measurement(value_source="figure", source_location="Fig. 3, digitized")
    ab = good_measurement(n=2, source_location="Abstract (Semantic Scholar; full text inaccessible): 1.2")
    found = rules(validate_records([make_record(measurements=[fig, ab])]))
    assert {"figure_not_high", "abstract_not_high"} <= found


def test_abstract_plus_results_quote_is_full_text():
    m = good_measurement(source_location="Abstract + Results: 1.2 W/mK at 30 wt%")
    assert validate_records([make_record(measurements=[m])]) == []


def test_duplicate_measurement_detected():
    a = good_measurement(n=1)
    b = good_measurement(n=2)  # same sample, condition and value, different id
    assert "duplicate_measurement" in rules(validate_records([make_record(measurements=[a, b])]))


def test_same_value_different_condition_is_not_duplicate():
    a = good_measurement(n=1, processing_method="Cured at ambient pressure")
    b = good_measurement(n=2, processing_method="Cured under 175 kPa")
    assert validate_records([make_record(measurements=[a, b])]) == []


def test_row_id_must_match_doi_hash():
    m = good_measurement(row_id="deadbeef-001")
    assert "row_id_format" in rules(validate_records([make_record(measurements=[m])]))


def test_row_id_unique_across_papers():
    doi2 = "10.1234/abc.2"
    r1 = make_record()
    r2 = make_record(doi=doi2, pid="P002", measurements=[good_measurement(doi2)])
    r2.measurements[0].row_id = r1.measurements[0].row_id
    assert "row_id_unique" in rules(validate_records([r1, r2]))


def test_tombstoned_row_cannot_return():
    rec = make_record()
    issues = validate_records([rec], tombstones=[rid("10.1234/abc.1", 1)])
    assert "tombstone_reused" in rules(issues)


def test_hybrid_label_warning():
    rec = make_record(measurements=[good_measurement(filler_material="Al2O3/BN")])
    issues = validate_records([rec])
    assert rules(issues) == {"hybrid_label"} and not errors(issues)


def test_bad_doi_and_year():
    rec = make_record(doi="doi:10.1/x", year=1850)
    rec.measurements[0].row_id = rid("doi:10.1/x", 1)
    assert {"doi_format", "year_range"} <= rules(validate_records([rec]))
