"""Course report: fingerprint guard, number formatting, reporting gaps, rendering."""
import json
import shutil

import pytest

from argus.fingerprint import StaleAnalysis, check_fresh, dataset_fingerprint
from argus.report.course import pct, reporting_gaps, sci


def test_sci_formatting():
    assert sci(6.81e-07) == "6.8×10⁻⁷"
    assert sci(2.4e-6) == "2.4×10⁻⁶"
    assert sci(1.0e3) == "1.0×10³"
    assert pct(0.982) == "98%"


def test_fingerprint_is_stable_and_sensitive(repo_layout):
    from argus.records import load_records

    recs = load_records(repo_layout).records
    a, b = dataset_fingerprint(recs), dataset_fingerprint(recs)
    assert a == b and a["rows"] >= 250
    recs[0].measurements[0].k_composite_W_mK += 0.01  # in-memory change only
    assert dataset_fingerprint(recs)["sha256"] != a["sha256"]


def test_stale_output_is_refused():
    cur = {"sha256": "abc"}
    check_fresh("x", {"dataset": {"sha256": "abc"}}, cur, "argus x")
    with pytest.raises(StaleAnalysis):
        check_fresh("x", {"dataset": {"sha256": "old"}}, cur, "argus x")
    with pytest.raises(StaleAnalysis):
        check_fresh("x", {}, cur, "argus x")


def test_reporting_gaps_counts():
    rows = [
        {"direction_reported": "unknown", "method_class": "LFA", "flags": "lfa_cp_rho_unreported",
         "k_matrix_basis": "reported", "filler_mean_size_um": "", "filler_alignment": "", "measurement_temperature_C": ""},
        {"direction_reported": "in-plane", "method_class": "UNSPECIFIED", "flags": "",
         "k_matrix_basis": "reference-default", "filler_mean_size_um": 5.0, "filler_alignment": "aligned",
         "measurement_temperature_C": 25.0},
    ]
    g = {x["item"]: x for x in reporting_gaps(rows)}
    assert g["Measurement direction (in-plane / through-plane)"]["missing"] == 1
    assert g["How Cp and density were obtained (laser-flash rows)"]["of"] == 1
    assert g["Neat-matrix k measured alongside"]["share"] == 0.5


def test_report_refuses_stale_analysis(repo_layout, tmp_path):
    """Copy the project's data and reports, tamper with one fingerprint, expect refusal."""
    pytest.importorskip("matplotlib")
    pytest.importorskip("jinja2")
    from argus.paths import Layout
    from argus.report.course import render

    if not (repo_layout.reports / "ml_benchmark.json").exists():
        pytest.skip("analysis outputs not generated")
    dst = tmp_path / "proj"
    shutil.copytree(repo_layout.data, dst / "data", ignore=shutil.ignore_patterns("processed"))
    shutil.copytree(repo_layout.reports, dst / "reports")
    p = dst / "reports" / "method_bias.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    d["dataset"]["sha256"] = "0000000000000000"
    p.write_text(json.dumps(d), encoding="utf-8")
    with pytest.raises(StaleAnalysis, match="method_bias"):
        render(Layout(dst), out=dst / "docs" / "COURSE_REPORT.md")


def test_report_renders_from_current_outputs(repo_layout, tmp_path):
    pytest.importorskip("matplotlib")
    pytest.importorskip("jinja2")
    from argus.report.course import build_context, render

    try:
        build_context(repo_layout, tmp_path / "figs", "figs")
    except StaleAnalysis as e:
        pytest.skip(f"analysis outputs are stale in this checkout: {e}")
    out = render(repo_layout, out=tmp_path / "COURSE_REPORT.md")
    text = out.read_text(encoding="utf-8")
    assert "## 4. Results" in text and "## References" in text
    assert "{{" not in text and "{%" not in text
    assert len(list((tmp_path / "figures").glob("fig*.png"))) == 7
    if (repo_layout.reports / "external_validation.json").exists():
        assert "### 4.5 Testing on data we did not curate" in text
        assert len(list((tmp_path / "figures").glob("external_*.png"))) == 2
