import json

import pytest
from conftest import good_measurement, make_record

from argus.build import BuildBlocked, build
from argus.io import dump_yaml, load_yaml
from argus.records import compile_rows, doi_slug, load_records, record_filename, save_record
from argus.schema import COLUMN_NAMES


def test_doi_slug_matches_legacy_fulltext_names():
    assert doi_slug("10.3390/polym10030340") == "10.3390_polym10030340"
    assert record_filename("P007", "10.1088/1757-899x/274/1/012043") == "P007_10.1088_1757-899x_274_1_012043.yaml"
    assert ":" not in doi_slug("10.1002/(sici)1097:4628")


def test_yaml_keeps_dates_and_numbers_exact():
    obj = {"date": "2026-10-13", "k": 0.1 + 0.2, "s": "yes", "n": "None", "u": "W m−1 K−1 · μm"}
    assert load_yaml_text(dump_yaml(obj)) == obj


def load_yaml_text(text, tmp=None):
    import io

    import yaml

    from argus.io import _Loader

    return yaml.load(io.StringIO(text), Loader=_Loader)


def test_hand_written_date_stays_string(tmp_path):
    p = tmp_path / "x.yaml"
    p.write_text("date_processed: 2026-10-13\n", encoding="utf-8")
    assert load_yaml(p) == {"date_processed": "2026-10-13"}


def test_record_roundtrip(tmp_project):
    rec = make_record()
    save_record(tmp_project, rec)
    res = load_records(tmp_project)
    assert not res.errors
    assert res.records[0] == rec


def test_unknown_field_is_a_schema_error(tmp_project):
    path = save_record(tmp_project, make_record())
    text = path.read_text(encoding="utf-8").replace("  confidence: High", "  confidence: High\n  confidense: High")
    path.write_text(text, encoding="utf-8")
    res = load_records(tmp_project)
    assert res.errors and "confidense" in res.errors[0][1]


def test_compiled_rows_have_all_columns_and_blanks():
    rows = compile_rows([make_record()])
    assert list(rows[0]) == list(COLUMN_NAMES)
    assert rows[0]["filler_mean_size_um"] == "" and rows[0]["doi"] == "10.1234/abc.1"


def test_build_is_deterministic(tmp_project):
    save_record(tmp_project, make_record())
    first = build(tmp_project)
    assert first.rows == 1 and first.written
    second = build(tmp_project)
    assert second.written == []  # nothing changed, nothing rewritten


def test_build_blocked_writes_nothing(tmp_project):
    save_record(tmp_project, make_record(measurements=[good_measurement(source_location="")]))
    with pytest.raises(BuildBlocked) as e:
        build(tmp_project)
    assert e.value.issues[0].rule == "source_location_present"
    assert not tmp_project.dataset_csv.exists()


def test_uncertain_csv_holds_exactly_non_high(tmp_project):
    ms = [good_measurement(n=1), good_measurement(n=2, confidence="Medium", filler_loading_wt_pct=40.0)]
    save_record(tmp_project, make_record(measurements=ms))
    r = build(tmp_project)
    assert (r.rows, r.uncertain) == (2, 1)
    rows = [json.loads(line) for line in tmp_project.compiled_jsonl.read_text(encoding="utf-8").splitlines()]
    assert [x["confidence"] for x in rows] == ["High", "Medium"]
