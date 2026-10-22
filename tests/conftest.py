from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from argus.paths import Layout, find_root
from argus.schema import Measurement, PaperMeta, PaperRecord

REPO = find_root(Path(__file__).parent)


def rid(doi: str, n: int) -> str:
    return f"{hashlib.md5(doi.encode()).hexdigest()[:8]}-{n:03d}"


def good_measurement(doi: str = "10.1234/abc.1", n: int = 1, **over) -> Measurement:
    base = dict(
        row_id=rid(doi, n), matrix_polymer="Epoxy", filler_material="h-BN",
        filler_loading_wt_pct=30.0, k_composite_W_mK=1.2, k_original_value=1.2,
        k_original_unit="W/mK", value_source="table", source_location="Table 2, EP/BN 30 wt%",
        confidence="High", k_direction="through-plane",
    )
    base.update(over)
    return Measurement(**base)


def make_record(doi: str = "10.1234/abc.1", pid: str = "P001", measurements=None, **paper) -> PaperRecord:
    meta = dict(doi=doi, title="A paper", year=2021, source_url=f"https://doi.org/{doi}")
    meta.update(paper)
    return PaperRecord(paper_id=pid, paper=PaperMeta(**meta),
                       measurements=measurements if measurements is not None else [good_measurement(doi)],
                       extraction_log=[{"seq": 1, "candidate_id": pid, "doi": doi}])


@pytest.fixture
def repo_layout() -> Layout:
    return Layout(REPO)


@pytest.fixture
def tmp_project(tmp_path: Path) -> Layout:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='t'\n")
    (tmp_path / "data" / "records").mkdir(parents=True)
    return Layout(tmp_path)
