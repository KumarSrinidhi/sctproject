"""Interactive explorer: payload, safe embedding, and the two page variants."""
import csv
import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from importlib import resources

import pytest

import argus.report.explorer as explorer
from argus.external.harmonize import normalize_doi
from argus.report.explorer import external_layer, filler_group, payload, provenance_group, safe_json

from conftest import REPO

DATA_RX = re.compile(r'<script type="application/json" id="argus-data">(.*?)</script>', re.S)
DOCUMENT_TAG_RX = re.compile(r"<(?:!doctype|html|head|body)[\s>]", re.I)  # not <header>
TOGGLE_RX = re.compile(r'<input type="checkbox" id="external"[^>]*>')
FOOTER_RX = re.compile(r"<footer>(.*?)</footer>", re.S)
NC_ND = {"ncomms", "heliyon"}
TAGP_SHARED_DOI = "10.1002/adfm.201900412"  # TAGP DS04 = ARGUS P081


def _payload_or_skip(lay):
    if not (lay.reports / "physics_summary.json").exists():
        pytest.skip("physics summary not generated")
    return payload(lay)


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


# ---------------------------------------------------------------- other groups' data layer

def test_external_layer_is_redistributable_and_new_to_argus(repo_layout):
    d = _payload_or_skip(repo_layout)
    ext, srcs = d["external"], d["external_sources"]
    assert ext, "the committed TAGP transcription always gives points"
    keys = {e["src"] for e in ext}
    assert keys <= {"evf", "tagp"} and set(srcs) == keys
    assert not (keys | set(srcs)) & NC_ND
    if importlib.util.find_spec("openpyxl"):
        assert "evf" in srcs
    for s in srcs.values():
        assert s["license"] in {"CC-BY-4.0", "MIT"} and s["license_url"].startswith("https://") and s["citation"]
    assert all(e["lic"] == srcs[e["src"]]["license"] for e in ext)
    # only literature ARGUS does not contain: TAGP DS04 (= ARGUS P081) is left out
    argus_dois = {normalize_doi(r["doi"]) for r in d["rows"]}
    assert TAGP_SHARED_DOI in argus_dois
    assert not {e["doi"] for e in ext} & argus_dois
    assert not any(e["ser"] == "DS04" for e in ext) and any(e["ser"] == "DS03" for e in ext)
    assert srcs["tagp"]["shared_with_argus"] > 0
    assert len({e["id"] for e in ext}) == len(ext) and not {e["id"] for e in ext} & {r["id"] for r in d["rows"]}
    assert all(e["phi"] > 0 and e["k"] > 0 for e in ext)
    assert sum(s["points"] for s in srcs.values()) == len(ext)
    # deterministic
    again, again_src = external_layer(repo_layout.data / "external", {r["doi"] for r in d["rows"]})
    assert again == ext and again_src == srcs


def _tagp_folder(tmp_path, license="CC-BY-4.0"):
    (tmp_path / "tagp").mkdir(parents=True)
    shutil.copy(REPO / "data" / "external" / "tagp" / "tagp_thermal_datasets.csv", tmp_path / "tagp")
    (tmp_path / "sources.yaml").write_text(
        "sources:\n"
        f"  tagp: {{title: T, authors: [Sarikhani, et al.], year: 2022, license: {license},\n"
        "         license_url: 'https://example.org/licence', url: 'javascript:alert(1)', citation: Cite me}\n"
        "  evf: {title: E, authors: [D A], year: 2026, license: CC-BY-4.0, citation: E}\n"
        "  ncomms: {title: N, license: CC-BY-NC-ND-4.0, citation: N}\n", encoding="utf-8")
    (tmp_path / "ncomms").mkdir(exist_ok=True)
    with (tmp_path / "tagp" / "tagp_thermal_datasets.csv").open(encoding="utf-8") as f:
        return [r for r in csv.DictReader(f) if float(r["vol_pct"]) > 0]


def test_external_layer_gates_licence_and_argus_papers(tmp_path):
    rows = _tagp_folder(tmp_path)
    pts, srcs = external_layer(tmp_path, {TAGP_SHARED_DOI.upper()})
    assert list(srcs) == ["tagp"] and {p["src"] for p in pts} == {"tagp"}
    assert {p["ser"] for p in pts} == {"DS03"} and len(pts) == sum(r["dataset"] == "DS03" for r in rows)
    assert srcs["tagp"]["shared_with_argus"] == sum(r["dataset"] == "DS04" for r in rows)
    assert srcs["tagp"]["url"] == ""  # only https links reach the page
    assert srcs["tagp"]["short"] == "Sarikhani et al. 2022" and srcs["tagp"]["license_label"] == "CC BY 4.0"
    assert [p["phi"] for p in pts] == sorted(p["phi"] for p in pts)
    # a non-redistributable licence keeps a source out entirely
    (tmp_path / "sources.yaml").unlink()
    shutil.rmtree(tmp_path / "tagp")
    _tagp_folder(tmp_path, license="CC-BY-NC-ND-4.0")
    assert external_layer(tmp_path, set()) == ([], {})


def test_external_layer_never_fails_on_missing_inputs(tmp_path, monkeypatch):
    assert external_layer(tmp_path / "absent", set()) == ([], {})
    _tagp_folder(tmp_path)
    (tmp_path / "evf").mkdir()  # folder without its workbook, and openpyxl unavailable
    monkeypatch.setitem(sys.modules, "openpyxl", None)
    with pytest.warns(UserWarning, match="evf"):
        pts, srcs = external_layer(tmp_path, set())
    assert list(srcs) == ["tagp"] and pts


def test_safe_json_escapes_the_real_payload(repo_layout):
    d = _payload_or_skip(repo_layout)
    s = safe_json(d)
    assert "<" not in s and ">" not in s and "&" not in s
    assert json.loads(s) == d
    if "evf" in d["external_sources"]:  # an SICI DOI carries literal < and >
        assert any("<" in e["doi"] for e in d["external"])


def test_render_with_external_layer(repo_layout, tmp_path):
    pytest.importorskip("jinja2")
    d = _payload_or_skip(repo_layout)
    paths = explorer.render(repo_layout, out_dir=tmp_path)
    full = paths["standalone"].read_text(encoding="utf-8")
    frag = paths["artifact"].read_text(encoding="utf-8")
    assert DOCUMENT_TAG_RX.search(frag) is None
    for page in (full, frag):
        toggle = TOGGLE_RX.search(page)
        assert toggle and "checked" not in toggle.group(0)  # off by default
        data = json.loads(DATA_RX.search(page).group(1))
        assert data["external"] == d["external"] and data["external_sources"] == d["external_sources"]
        footer = FOOTER_RX.search(page).group(1)
        for s in d["external_sources"].values():
            assert html.escape(s["citation"], quote=False) in footer and f'href="{s["license_url"]}"' in footer
        assert "not part of the ARGUS dataset" in footer


def test_render_without_external_data_has_no_toggle(repo_layout, tmp_path, monkeypatch):
    pytest.importorskip("jinja2")
    _payload_or_skip(repo_layout)
    monkeypatch.setattr(explorer, "external_layer", lambda *a, **k: ([], {}))
    paths = explorer.render(repo_layout, out_dir=tmp_path)
    for page in (paths["standalone"].read_text(encoding="utf-8"), paths["artifact"].read_text(encoding="utf-8")):
        assert 'id="external"' not in page
        assert "Other groups" not in FOOTER_RX.search(page).group(1)
        data = json.loads(DATA_RX.search(page).group(1))
        assert data["external"] == [] and data["external_sources"] == {}
    assert DOCUMENT_TAG_RX.search(paths["artifact"].read_text(encoding="utf-8")) is None
