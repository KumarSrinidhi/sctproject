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
    assert not nc, f"non-commercial full texts must not be stored in the repository: {nc}"


def test_known_licences_are_detected(tmp_path):
    from argus.paths import Layout

    ft = tmp_path / "work" / "fulltext"
    ft.mkdir(parents=True)
    # wording as it appears in the papers that used to be stored here
    (ft / "a.txt").write_text("distributed under the terms of the Creative Commons Attribution Non-Commercial "
                              "License (http://creative-\ncommons.org/licenses/by-nc/3.0) which permits",
                              encoding="utf-8")  # URL split across a line break (as in 10.3740/mrsk.2023.33.12.503)
    (ft / "b.txt").write_text("Creative Commons Attribution-NonCommercial 4.0 License "
                              "(https://creativecommons.org/licenses/by-nc/4.0/)", encoding="utf-8")
    (ft / "c.txt").write_text("distributed under the Creative Commons Attribution (CC BY) license "
                              "(https://creativecommons.org/licenses/by/4.0/)", encoding="utf-8")
    (ft / "d.txt").write_text("All rights reserved.", encoding="utf-8")
    lic = fulltext_licences(Layout(tmp_path))
    assert lic == {"a": ("NC", "3.0"), "b": ("NC", "4.0"), "c": ("BY", "4.0"), "d": ("none", None)}


def test_every_stored_third_party_file_is_cc_by_and_inventoried(repo_layout):
    import csv
    import subprocess

    inv = {r["path"]: r for r in csv.DictReader(open(repo_layout.legacy / "THIRD_PARTY.csv", encoding="utf-8"))}
    try:
        tracked = subprocess.run(["git", "ls-files", "work/fulltext", "work/phase4_browser", "work/figures"],
                                 cwd=repo_layout.root, capture_output=True, text=True, check=True,
                                 stdin=subprocess.DEVNULL).stdout.split()  # pytest's stdin handle is invalid on Windows
    except (OSError, subprocess.CalledProcessError) as e:
        pytest.skip(f"not a git checkout ({type(e).__name__}: {getattr(e, 'stderr', '') or e})")
    assert tracked, "expected tracked third-party files"
    missing = [p for p in tracked if p not in inv]
    assert not missing, f"third-party files without a licence entry in work/THIRD_PARTY.csv: {missing}"
    assert all(inv[p]["licence"] == "CC BY" and inv[p]["evidence"] for p in tracked)
    stale = [p for p in inv if p not in tracked]
    assert not stale, f"work/THIRD_PARTY.csv lists files that are not in the repository: {stale}"


def test_datapackage_carries_licence_and_authors(repo_layout):
    d = json.loads((repo_layout.root / "datapackage.json").read_text(encoding="utf-8"))
    assert d["licenses"][0]["name"] == "CC-BY-4.0"
    assert [c["title"] for c in d["contributors"]] == author_names(dataset_meta(repo_layout))


def test_toolkit_version_is_consistent(repo_layout):
    py = (repo_layout.root / "pyproject.toml").read_text(encoding="utf-8")
    assert f'version = "{__version__}"' in py


def test_zenodo_metadata_matches_dataset_yaml(repo_layout):
    from argus.release import zenodo_metadata

    meta = dataset_meta(repo_layout)
    z = zenodo_metadata(meta)
    assert z["upload_type"] == "dataset" and z["license"] == "cc-by-4.0" and z["version"] == meta["version"]
    assert [c["name"] for c in z["creators"]] == ["Kumar, Aniket", "Reddy, Rao Kumar Srinidhi"]
    assert z["publication_date"] == str(meta["released"]) and z["keywords"] == meta["keywords"]
    committed = json.loads((repo_layout.root / ".zenodo.json").read_text(encoding="utf-8"))
    assert committed == z, "run `argus build` to regenerate .zenodo.json"


def test_doi_flows_into_citation_files():
    from argus.release import zenodo_metadata

    meta = {"title": "T", "version": "1.2.0", "released": "2027-01-01", "license": "CC-BY-4.0",
            "authors": [{"given-names": "Aniket", "family-names": "Kumar"}], "homepage": "https://example.org",
            "doi": "10.5281/zenodo.123", "publisher": "Zenodo"}
    assert citation_text(meta).endswith("[Data set]. Zenodo. https://doi.org/10.5281/zenodo.123")
    assert 'doi: "10.5281/zenodo.123"' in citation_cff(meta)
    assert zenodo_metadata(meta)["doi"] == "10.5281/zenodo.123"


def test_bundle_is_reproducible_and_holds_only_dataset_files(repo_layout, tmp_path):
    import hashlib
    import zipfile

    from argus.release import build_bundle

    p1, h1 = build_bundle(repo_layout, tmp_path / "a")
    p2, h2 = build_bundle(repo_layout, tmp_path / "b")
    assert h1 == h2 and p1.read_bytes() == p2.read_bytes()
    names = zipfile.ZipFile(p1).namelist()
    top = names[0].split("/")[0]
    rel = [n.split("/", 1)[1] for n in names]
    assert top == f"ARGUS-dataset-v{dataset_meta(repo_layout)['version']}"
    assert "thermal_conductivity_dataset.csv" in rel and "datapackage.json" in rel and "SHA256SUMS.txt" in rel
    assert not any(r.startswith(("work/", "src/", "tests/", "local_archive/", "data/external/")) for r in rel)
    assert not any("OPENALEX" in r or r.endswith((".py", ".pdf")) for r in rel)
    z = zipfile.ZipFile(p1)
    sums = dict(line.split("  ", 1)[::-1] for line in z.read(f"{top}/SHA256SUMS.txt").decode().splitlines())
    for r in rel:
        if r != "SHA256SUMS.txt":
            assert hashlib.sha256(z.read(f"{top}/{r}")).hexdigest() == sums[r]


def test_canonical_bytes_pins_line_endings():
    from argus.release import canonical_bytes

    assert canonical_bytes("a.csv", b"x,y\nz,w\r\n") == b"x,y\r\nz,w\r\n"
    assert canonical_bytes("data/records/P1.yaml", b"a: 1\r\nb: 2\n") == b"a: 1\nb: 2\n"
    assert canonical_bytes("LICENSE-DATA.md", b"t\r\n") == b"t\n"
    assert canonical_bytes("img.png", b"\x89PNG\r\n") == b"\x89PNG\r\n"  # binary untouched


def test_bundle_does_not_depend_on_checkout_line_endings(repo_layout, tmp_path):
    """A Windows checkout (core.autocrlf=true) mixes CRLF files from git with LF files written
    by the toolkit; the bundle must come out byte-identical to an LF checkout's."""
    import shutil

    from argus.paths import Layout
    from argus.release import build_bundle, bundle_members

    members = bundle_members(repo_layout)
    hashes = []
    for i, eol in enumerate((b"\n", b"\r\n")):
        root = tmp_path / f"checkout{i}"
        for j, m in enumerate(members):
            dst = root / m
            dst.parent.mkdir(parents=True, exist_ok=True)
            raw = (repo_layout.root / m).read_bytes().replace(b"\r\n", b"\n")
            # every other file flips to the other convention, like a partly rewritten checkout
            mixed = eol if j % 2 else (b"\r\n" if eol == b"\n" else b"\n")
            dst.write_bytes(raw.replace(b"\n", mixed))
        shutil.copy(repo_layout.root / "pyproject.toml", root / "pyproject.toml")
        hashes.append(build_bundle(Layout(root), tmp_path / f"out{i}")[1])
    assert hashes[0] == hashes[1]


def test_bundle_carries_its_own_licence_not_the_repository_one(repo_layout, tmp_path):
    import zipfile

    from argus.release import build_bundle

    path, _ = build_bundle(repo_layout, tmp_path)
    z = zipfile.ZipFile(path)
    top = z.namelist()[0].split("/")[0]
    rel = [n.split("/", 1)[1] for n in z.namelist()]
    assert "LICENSE.txt" in rel and "LICENSE-DATA.md" not in rel  # the repo file describes code, work/, ...
    lic = z.read(f"{top}/LICENSE.txt").decode("utf-8")
    meta = dataset_meta(repo_layout)
    assert meta["license"] in lic and meta["version"] in lic
    assert "Quoted passages" in lic and "qc_findings" in lic and "no code" in lic
    readme = z.read(f"{top}/README.txt").decode("utf-8")
    assert "(see LICENSE.txt)" in readme and "  LICENSE.txt" in readme


def test_datapackage_declares_every_published_table(repo_layout):
    from argus.release import BUNDLE_FILES

    pkg = json.loads((repo_layout.root / "datapackage.json").read_text(encoding="utf-8"))
    paths = {r["path"] for r in pkg["resources"]}
    assert {f for f in BUNDLE_FILES if f.endswith(".csv")} <= paths
    assert pkg["title"].startswith("ARGUS: ")
