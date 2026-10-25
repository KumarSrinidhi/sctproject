"""Phase 6 acquisition: key handling, screening rules, quote checks, JATS rendering."""
from __future__ import annotations

import pytest

from argus.acquire.keys import MissingKey, openalex_key, redact
from argus.acquire.openalex import abstract_text, work_record
from argus.acquire.quotes import norm, number_in_quote, quote_in_source
from argus.acquire.screen import decide


def test_key_from_env_or_file_and_never_shown(tmp_path, monkeypatch):
    monkeypatch.delenv("OPENALEX_API_KEY", raising=False)
    with pytest.raises(MissingKey):
        openalex_key(tmp_path)
    (tmp_path / "OPENALEX_API_KEY.txt").write_text("  secret123  \n", encoding="utf-8")
    assert openalex_key(tmp_path) == "secret123"
    monkeypatch.setenv("OPENALEX_API_KEY", "fromenv")
    assert openalex_key(tmp_path) == "fromenv"
    assert "secret123" not in redact("https://api.openalex.org/works?search=x&api_key=secret123&per_page=5")
    assert redact("token secret123 here", "secret123") == "token <redacted> here"


def test_key_file_is_git_ignored():
    from pathlib import Path

    ignore = (Path(__file__).resolve().parents[1] / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert "OPENALEX_API_KEY.txt" in ignore and "sources/" in ignore


def test_abstract_rebuilt_from_inverted_index():
    assert abstract_text({"thermal": [0], "conductivity": [1], "of": [2], "BN": [3]}) == "thermal conductivity of BN"
    assert abstract_text(None) == ""


def test_work_record_normalizes_doi_and_licence():
    w = {"doi": "https://doi.org/10.3390/POLYM1", "title": " A  title ", "publication_year": 2020, "type": "article",
         "best_oa_location": {"license": "cc-by", "pdf_url": "https://x/y.pdf"}, "ids": {}, "open_access": {"oa_status": "gold"}}
    r = work_record(w)
    assert r["doi"] == "10.3390/polym1" and r["title"] == "A title" and r["license"] == "cc-by" and r["pmcid"] == ""


def _c(**kw):
    base = {"doi": "10.1/x", "type": "article", "license": "cc-by", "title": "Epoxy/BN composites with high thermal conductivity",
            "abstract": "We prepared epoxy filled with 30 wt% boron nitride and measured k by laser flash."}
    base.update(kw)
    return base


@pytest.mark.parametrize("kw,code", [
    ({}, "include"),
    ({"doi": ""}, "no-doi"),
    ({"type": "review"}, "review"),
    ({"title": "A review of boron nitride polymer composites"}, "review"),
    ({"title": "Epoxy/BN composites", "abstract": "mechanical properties of epoxy filled with boron nitride"}, "no-k"),
    ({"title": "Epoxy/graphene thermal conductivity", "abstract": "graphene in epoxy raises thermal conductivity"}, "no-target-filler"),
    ({"title": "Sintered AlN ceramics thermal conductivity", "abstract": "sintered aluminium nitride thermal conductivity"}, "no-polymer"),
    ({"license": "cc-by-nc-nd"}, "include"),
    ({"license": ""}, "not-open"),
])
def test_screening_rules(kw, code):
    assert decide(_c(**kw), set(), set()) == code


def test_screening_skips_known_papers():
    assert decide(_c(), {"10.1/x"}, set()) == "already-in-argus"
    assert decide(_c(), set(), {"10.1/x"}) == "already-screened"


def test_quote_check_tolerates_only_harmless_differences():
    src = "Table 2 | PP/PDA-hBN-30 | 30 | 1.25 ± 0.03\nThe k of neat PP was 0.21 W/(m·K)."
    assert quote_in_source("PP/PDA-hBN-30 | 30 | 1.25 ± 0.03", src)
    assert quote_in_source("pp/pda-hbn-30|30|1.25 ± 0.03", src)  # case and separator spacing
    assert quote_in_source("The k of neat PP was 0.21 W/(m·K).", src)
    assert not quote_in_source("The k of neat PP was 0.23 W/(m·K).", src)
    assert not quote_in_source("", src)
    assert norm("1.2–3.4") == norm("1.2-3.4")
    assert number_in_quote(1.25, "| 30 | 1.25 ± 0.03") and not number_in_quote(1.26, "| 30 | 1.25 ± 0.03")


def test_jats_rendering_keeps_tables_as_rows(tmp_path):
    from argus.acquire.europepmc import render

    xml = """<article xmlns:xlink="http://www.w3.org/1999/xlink"><front><article-meta>
      <title-group><article-title>BN/epoxy</article-title></title-group>
      <permissions><license xlink:href="https://creativecommons.org/licenses/by/4.0/"><p>CC BY</p></license></permissions>
      <abstract><p>Abstract text.</p></abstract></article-meta></front>
      <body><sec><title>Results</title><p>The k reached 1.2 W/mK.</p>
      <table-wrap><label>Table 1</label><caption><p>Thermal conductivity.</p></caption>
      <table><tr><th>Sample</th><th>k</th></tr><tr><td>EP-30</td><td>1.2</td></tr></table></table-wrap></sec></body></article>"""
    p = tmp_path / "a.xml"
    p.write_text(xml, encoding="utf-8")
    r = render(p)
    assert r["title"] == "BN/epoxy" and r["licence"] == "https://creativecommons.org/licenses/by/4.0/"
    assert "# Results" in r["text"] and "EP-30 | 1.2" in r["text"] and "[Table 1] Thermal conductivity." in r["text"]


def test_importer_applies_verdicts_and_provenance_checks(tmp_project):
    from argus.acquire.importer import import_batch
    from argus.records import load_records

    lay = tmp_project
    text_dir = lay.root / "sources" / "text"
    text_dir.mkdir(parents=True)
    doi = "10.9999/new.1"
    (text_dir / "10.9999_new.1.txt").write_text(
        "[Table 1] Thermal conductivity.\nEP-0 | 0 | 0.20\nEP-BN-30 | 30 | 1.25\nEP-BN-40 | 40 | 1.90\n", encoding="utf-8")
    row = dict(matrix_polymer="epoxy", filler_material="BN", filler_loading_vol_pct=None, filler_loading_wt_pct=30,
               filler_loading_original_value=30, filler_loading_original_unit="wt%", k_composite_W_mK=1.25,
               k_direction="unknown", measurement_method="laser flash", k_original_value=1.25, k_original_unit="W/(m K)",
               value_source="table", confidence="High", quote="EP-BN-30 | 30 | 1.25", location="Table 1", notes=None)
    bad = dict(row, k_composite_W_mK=1.3, k_original_value=1.3, quote="EP-BN-30 | 30 | 1.30")   # not verbatim
    wrong = dict(row, filler_loading_wt_pct=40, filler_loading_original_value=40, k_composite_W_mK=1.9,
                 k_original_value=1.9, quote="EP-BN-40 | 40 | 1.90")
    papers = [{"doi": doi, "usable": True, "reason_if_not_usable": "", "title_as_printed": "New BN paper", "year": 2024,
               "tables_inspected": "Table 1", "figures_inspected": "", "figure_only_skipped": 0,
               "measurements": [row, bad, wrong], "extraction_notes": ""},
              {"doi": "10.9999/review.2", "usable": False, "reason_if_not_usable": "review article",
               "title_as_printed": "A review", "year": 2024, "tables_inspected": "", "figures_inspected": "",
               "figure_only_skipped": 0, "measurements": [], "extraction_notes": ""}]
    (text_dir / "10.9999_review.2.txt").write_text("review", encoding="utf-8")
    verdicts = {doi: {"doi": doi, "usable_agreed": True, "notes": "",
                      "rows": [{"index": 0, "verdict": "accept", "quote_verbatim": True, "corrections": {}, "reason": ""},
                               {"index": 1, "verdict": "accept", "quote_verbatim": False, "corrections": {}, "reason": ""},
                               {"index": 2, "verdict": "reject", "quote_verbatim": True, "corrections": {}, "reason": "duplicate"}],
                      "missed": [dict(row, filler_material="none", filler_loading_wt_pct=0, filler_loading_original_value=0,
                                      k_composite_W_mK=0.2, k_original_value=0.2, quote="EP-0 | 0 | 0.20")]}}
    rep = import_batch(lay, papers, verdicts, {}, text_dir)
    assert rep.rows_added == 2 and len(rep.created) == 1
    assert {why for _, _, why in rep.rejected} == {"verifier: duplicate", "quote not found verbatim in the source"}
    assert rep.excluded == [("10.9999/review.2", "Phase 6 screening of full text: review article")]
    rec = [r for r in load_records(lay).records if r.paper.doi == doi][0]
    ks = sorted(m.k_composite_W_mK for m in rec.measurements)
    assert ks == [0.2, 1.25]
    assert all(m.source_location.startswith("Table 1: '") for m in rec.measurements)
    assert any("independent verifier" in (m.notes or "") for m in rec.measurements)
