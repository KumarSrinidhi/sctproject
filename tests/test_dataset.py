"""Checks against the real curated dataset in data/."""
import pytest

from argus.build import expected_outputs, tombstone_ids
from argus.legacy import verify_migration
from argus.records import load_records
from argus.validate import errors, validate_records


@pytest.fixture(scope="module")
def loaded(request):
    from conftest import REPO

    from argus.paths import Layout

    lay = Layout(REPO)
    return lay, load_records(lay)


def test_records_parse(loaded):
    _, res = loaded
    assert not res.errors
    assert len(res.records) >= 95


def test_no_validation_errors(loaded):
    lay, res = loaded
    errs = errors(validate_records(res.records, tombstone_ids(lay)))
    assert not errs, [f"{e.paper_id} {e.row_id} {e.rule}: {e.message}" for e in errs[:10]]


def test_deliverables_match_a_fresh_build(loaded):
    lay, _ = loaded
    stale = [p.name for p, data in expected_outputs(lay).items() if p.read_bytes() != data]
    assert not stale, f"run `argus build`: {stale}"


def test_paper_ids_unique_and_sequential(loaded):
    _, res = loaded
    ids = [r.paper_id for r in res.records]
    assert len(ids) == len(set(ids))
    assert ids == sorted(ids)


def test_one_record_per_doi(loaded):
    _, res = loaded
    dois = [r.paper.doi.lower() for r in res.records]
    assert len(dois) == len(set(dois))


def test_every_change_since_legacy_is_declared(loaded):
    lay, _ = loaded
    if not lay.legacy_rows.exists():
        pytest.skip("legacy work/ folder not present")
    from argus.legacy import undeclared_legacy_diffs

    assert undeclared_legacy_diffs(lay) == []


def test_undeclared_edit_is_caught(loaded, tmp_path):
    """Copy the project, silently edit one value, and expect the check to flag it."""
    import shutil

    from argus.legacy import undeclared_legacy_diffs
    from argus.paths import Layout

    lay, _ = loaded
    if not lay.legacy_rows.exists():
        pytest.skip("legacy work/ folder not present")
    dst = tmp_path / "proj"
    shutil.copytree(lay.data, dst / "data", ignore=shutil.ignore_patterns("processed"))
    (dst / "work").mkdir()
    shutil.copy(lay.legacy_rows, dst / "work" / "rows_raw.jsonl")
    p = dst / "data" / "records" / "P001_10.3390_polym10030340.yaml"
    p.write_text(p.read_text(encoding="utf-8").replace("k_composite_W_mK: 0.8\n", "k_composite_W_mK: 0.9\n", 1),
                 encoding="utf-8")
    diffs = undeclared_legacy_diffs(Layout(dst))
    assert diffs == ["b450fec2-001: k_composite_W_mK changed without a declaration"]


def test_fresh_migration_is_lossless(loaded, tmp_path):
    """Re-running the migration from work/ reproduces the legacy rows exactly."""
    import shutil

    from argus.legacy import migrate
    from argus.paths import Layout

    lay, _ = loaded
    if not lay.legacy_rows.exists():
        pytest.skip("legacy work/ folder not present")
    dst = Layout(tmp_path / "proj")
    (dst.root / "work").mkdir(parents=True)
    for f in ("rows_raw.jsonl", "extraction_log.jsonl", "phase2_applied_changes.json"):
        shutil.copy(lay.legacy / f, dst.legacy / f)
    # the published v1.0 exclusion list is the migration input
    shutil.copy(lay.legacy / "backup_final" / "unusable_sources.csv", dst.unusable_csv)
    migrate(dst)
    assert verify_migration(dst) == []
