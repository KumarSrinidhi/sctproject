"""Release metadata: CITATION.cff, licences and version consistency."""
import json

import pytest
import yaml

from argus import __version__
from argus.release import author_names, citation_cff, citation_text, dataset_meta, fulltext_licences


def test_citation_cff_round_trips_and_matches_dataset_yaml(repo_layout):
    meta = dataset_meta(repo_layout)
    cff = yaml.safe_load(citation_cff(meta))
    assert cff["cff-version"] == "1.2.0" and cff["type"] == "dataset"
    assert cff["version"] == meta["version"] and cff["date-released"] == str(meta["released"])
    assert [f"{a['given-names']} {a['family-names']}" for a in cff["authors"]] == author_names(meta)
    # only the data licence: a CFF licence list means "any of", which would offer the data under MIT
    assert cff["license"] == meta["license"] == "CC-BY-4.0"
    assert meta["code_license"] in cff["message"]


def test_citation_cff_is_robust_to_missing_fields():
    cff = yaml.safe_load(citation_cff({"title": "T", "authors": [{"family-names": "Curie"}]}))
    assert "license" not in cff and cff["authors"] == [{"family-names": "Curie"}]
    with pytest.raises(ValueError):
        citation_cff({"title": "T", "authors": [{}]})


def test_committed_citation_file_is_the_generated_one(repo_layout):
    meta = dataset_meta(repo_layout)
    assert (repo_layout.root / "CITATION.cff").read_text(encoding="utf-8") == citation_cff(meta)


def test_citation_text_formats_initials():
    meta = {"authors": [{"given-names": "Aniket", "family-names": "Kumar"},
                        {"given-names": "Rao Kumar Srinidhi", "family-names": "Reddy"}],
            "released": "2026-10-22", "title": "T", "version": "1.1.0", "homepage": "https://x"}
    assert citation_text(meta).startswith("Kumar, A., & Reddy, R. K. S. (2026). ARGUS: T (Version 1.1.0)")


def test_hand_written_citations_match_the_generated_one(repo_layout):
    cite = citation_text(dataset_meta(repo_layout))
    for name in ("README.md", "LICENSE-DATA.md"):
        assert cite in (repo_layout.root / name).read_text(encoding="utf-8"), name
    title = "ARGUS: " + dataset_meta(repo_layout)["title"]
    assert title in (repo_layout.root / "LICENSE-DATA.md").read_text(encoding="utf-8")


def test_licence_files_present_and_scoped(repo_layout):
    lic = (repo_layout.root / "LICENSE").read_text(encoding="utf-8")
    data = (repo_layout.root / "LICENSE-DATA.md").read_text(encoding="utf-8")
    assert lic.startswith("MIT License") and "Aniket Kumar" in lic and "Rao Kumar Srinidhi Reddy" in lic
    assert lic.rstrip().endswith("SOFTWARE."), "keep LICENSE pure MIT text so GitHub detects it"
    assert "CC BY 4.0" in data and "creativecommons.org/licenses/by/4.0" in data
    assert "work/fulltext/" in data  # third-party papers explicitly excluded


def test_licence_statement_counts_match_the_stored_full_texts(repo_layout):
    lic = fulltext_licences(repo_layout)
    if not lic:
        pytest.skip("no stored full texts")
    by = [s for s, (k, _) in lic.items() if k == "BY"]
    nc = [s for s, (k, _) in lic.items() if k == "NC"]
    none = [s for s, (k, _) in lic.items() if k == "none"]
    data = (repo_layout.root / "LICENSE-DATA.md").read_text(encoding="utf-8")
    assert f"Of the {len(lic)} stored full texts (`*.txt`), {len(by)} state a CC BY licence" in data
    assert f"The other {len(none)} do not state a licence" in data
    assert all(stem in data for stem in nc) and len(nc) == 2


def test_known_licences_are_detected(repo_layout):
    lic = fulltext_licences(repo_layout)
    if not lic:
        pytest.skip("no stored full texts")
    assert lic.get("10.3740_mrsk.2023.33.12.503") == ("NC", "3.0")  # URL split across a line break
    assert lic.get("10.1177_09673911221110143") == ("NC", "4.0")


def test_datapackage_carries_licence_and_authors(repo_layout):
    d = json.loads((repo_layout.root / "datapackage.json").read_text(encoding="utf-8"))
    assert d["licenses"][0]["name"] == "CC-BY-4.0"
    assert [c["title"] for c in d["contributors"]] == author_names(dataset_meta(repo_layout))


def test_toolkit_version_is_consistent(repo_layout):
    py = (repo_layout.root / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{__version__}"' in py
