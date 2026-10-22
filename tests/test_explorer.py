"""Interactive explorer: payload, safe embedding, and the two page variants."""
import json
import re
import shutil
import subprocess
from importlib import resources

import pytest

from argus.report.explorer import filler_group, payload, provenance_group, safe_json

DATA_RX = re.compile(r'<script type="application/json" id="argus-data">(.*?)</script>', re.S)


def test_safe_json_cannot_close_its_script_element():
    evil = {"sl": "</script><script>alert(1)</script>", "amp": "a & b", "ls": "x y"}
    s = safe_json(evil)
    assert "</script" not in s.lower() and "<" not in s and ">" not in s and "&" not in s
    assert json.loads(s) == evil


def test_group_mappings():
    base = {"is_hybrid": False, "filler_family": "BN", "filler_base": "h-BN", "flags": ""}
    assert filler_group(base) == "hBN"
    assert filler_group({**base, "filler_base": "BNNS"}) == "BNNS"
    assert filler_group({**base, "filler_base": "MgO", "filler_family": "MgO"}) == "oxide"
    assert filler_group({**base, "is_hybrid": "true"}) == "hybrid"
    assert filler_group({**base, "filler_family": "none", "filler_base": ""}) == "neat"
    assert provenance_group({"flags": "abstract_only;method_unspecified"}) == "abstract"
    assert provenance_group({"flags": "figure_digitized"}) == "figure"
    assert provenance_group({"flags": ""}) == "fulltext"


def test_payload_matches_dataset(repo_layout):
    if not (repo_layout.reports / "physics_summary.json").exists():
        pytest.skip("physics summary not generated")
    d = payload(repo_layout)
    assert len(d["rows"]) == d["meta"]["rows"] >= 250
    assert len({r["id"] for r in d["rows"]}) == len(d["rows"])
    assert all(r["k"] > 0 for r in d["rows"])
    c = d["curves"]
    assert len(c["phi"]) == len(c["ceiling"]) == len(c["nan0"]) == len(c["nanr"])
    # physics ordering at every loading: ceiling (spheres) < perfect-interface platelets
    assert all(a < b for a, b in zip(c["ceiling"][5:], c["nan0"][5:]) if a and b)


def test_explorer_script_has_no_closing_tag_and_parses():
    js = resources.files("argus").joinpath("report/templates/explorer.js").read_text(encoding="utf-8")
    assert "</script" not in js.lower() and "<!--" not in js
    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    res = subprocess.run([node, "--check", "-"], input=js, capture_output=True, text=True, encoding="utf-8")
    assert res.returncode == 0, res.stderr


def test_render_writes_standalone_and_artifact_variants(repo_layout, tmp_path):
    pytest.importorskip("jinja2")
    if not (repo_layout.reports / "physics_summary.json").exists():
        pytest.skip("physics summary not generated")
    from argus.report.explorer import render

    paths = render(repo_layout, out_dir=tmp_path)
    full = paths["standalone"].read_text(encoding="utf-8")
    frag = paths["artifact"].read_text(encoding="utf-8")
    assert full.startswith("<!doctype html>") and "</html>" in full
    for tag in ("<!doctype", "<html", "<head>", "<body"):
        assert tag not in frag.lower()
    for page in (full, frag):
        assert "<title>ARGUS Conductivity Explorer</title>" in page[:8192]
        assert "ARGUS_DATA" not in page and "ARGUS_SCRIPT" not in page
        data = json.loads(DATA_RX.search(page).group(1))
        assert len(data["rows"]) == data["meta"]["rows"]
    assert len(frag.encode("utf-8")) < 16 * 1024 * 1024
