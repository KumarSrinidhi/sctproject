"""External-data layer: harmonizing, cross-checking and transfer validation."""
from __future__ import annotations

import numpy as np
import pytest

from argus.external.crosscheck import crosscheck
from argus.external.harmonize import (ExternalRecord, enrich_external, filler_class, normalize_doi,
                                      normalize_filler, to_row)
from argus.schema import COLUMN_NAMES


@pytest.mark.parametrize("raw,label", [
    ("hexagonal boron nitride", "h-BN"), ("h-BN", "h-BN"), ("hBN", "h-BN"), ("BN nanosheets", "BNNS"),
    ("boron nitride (h-BN)", "h-BN"), ("Aluminum nitride", "AlN"), ("aluminium nitride", "AlN"),
    ("alumina", "Al2O3"), ("Al2O3", "Al2O3"), ("magnesium oxide", "MgO"), ("silicon carbide", "SiC"),
    ("BN + Al2O3", "BN/Al2O3 hybrid"), ("graphene nanoplatelets", "graphene"), ("neat", "none"),
    ("aluminium", "Al"), ("mystery filler", "mystery filler"),
])
def test_normalize_filler(raw, label):
    assert normalize_filler(raw) == label


def test_filler_class():
    assert filler_class("AlN") == "ceramic"
    assert filler_class("graphene") == "carbon"
    assert filler_class("BN/AlN hybrid") == "hybrid"
    assert filler_class("mystery filler") == "unknown"


def test_normalize_doi():
    assert normalize_doi("https://doi.org/10.1016/J.X.2020.1.") == "10.1016/j.x.2020.1"
    assert normalize_doi("doi: 10.3390/POLYM1") == "10.3390/polym1"


def _rec(**kw):
    base = dict(source="t", ext_id="1", k=1.0, filler="h-BN", matrix="epoxy", doi="10.1/a", vol_pct=20.0)
    base.update(kw)
    return ExternalRecord(**base)


def test_row_has_argus_columns_and_enriches_like_argus():
    row = to_row(_rec(wt_pct=None))
    assert tuple(row) == tuple(COLUMN_NAMES) and row["confidence"] == "External"
    (e,) = enrich_external([_rec(vol_pct=None, wt_pct=30.0, method="laser flash")])
    assert e["phi_basis"] == "converted-from-wt" and 18 < e["phi_vol_pct"] < 20
    assert e["method_class"] == "LFA" and e["k_matrix_basis"] == "reference-default"
    assert e["paper_id"].startswith("X") and e["ext_source"] == "t"


def _argus(rid, doi, phi, k, filler="h-BN", direction="unknown"):
    return {"row_id": rid, "doi": doi, "phi_vol_pct": phi, "k_composite_W_mK": k, "filler_material": filler,
            "direction_reported": direction, "phi_basis": "reported", "value_source": "table", "confidence": "High"}


def test_crosscheck_pairs_grades_and_leftovers():
    argus = [_argus("a1", "10.1/a", 10, 0.50), _argus("a2", "10.1/a", 20, 1.00), _argus("a3", "10.1/a", 30, 2.0),
             _argus("b1", "10.1/b", 10, 0.4)]
    ext = enrich_external([_rec(ext_id="1", vol_pct=10.3, k=0.51), _rec(ext_id="2", vol_pct=20, k=1.10),
                           _rec(ext_id="3", vol_pct=20, k=1.5, direction="in-plane"),
                           _rec(ext_id="4", vol_pct=45, k=3.0), _rec(ext_id="5", doi="10.1/zzz", k=9.0)])
    # ext 3 is in-plane vs unknown -> compatible; it pairs with a2 too (closest loading)
    res = crosscheck(ext, argus)
    assert res["shared_papers"] == 1 and res["shared_dois"] == ["10.1/a"]
    grades = {p["ext_row"]: p["grade"] for p in res["pair_rows"]}
    assert grades["t-1"] == "agree" and grades["t-2"] == "minor" and grades["t-3"] == "disagree"
    assert [u["ext_row"] for u in res["unmatched_external"]] == ["t-4"]
    assert [u["argus_row"] for u in res["unmatched_argus"]] == ["a3"]


def test_crosscheck_respects_direction_and_filler():
    argus = [_argus("a1", "10.1/a", 20, 1.0, direction="through-plane")]
    ext = enrich_external([_rec(vol_pct=20, k=5.0, direction="in-plane"), _rec(ext_id="2", vol_pct=20, filler="AlN")])
    res = crosscheck(ext, argus)
    assert res["pairs"] == 0 and len(res["unmatched_external"]) == 2


def test_transfer_runs_and_reports_coverage():
    pytest.importorskip("sklearn")
    from argus.external.transfer import transfer
    from argus.ml.features import Dataset

    rng = np.random.default_rng(0)
    names = ["phys_nan", "phi", "f_BNNS", "f_AlN", "f_oxide"]

    def ds(n, papers):
        X = rng.uniform(0, 1, (n, len(names)))
        y = 0.8 * X[:, 0] + 0.1 * rng.normal(size=n)
        g = np.array([f"P{i % papers}" for i in range(n)])
        rows = [{"filler_base": "h-BN", "matrix_family": "epoxy"} for _ in range(n)]
        return Dataset(X=X, y=y, groups=g, names=names, rows=rows)

    res = transfer(ds(60, 12), ds(20, 5), models=("median", "physics"))
    assert res["ranking_test_mae"][0] == "physics"
    iv = res["models"]["physics"]["interval"]
    assert 0 <= iv["coverage"] <= 1 and iv["half_width_log10"] > 0
    assert res["models"]["physics"]["by_filler"]["h-BN"]["n"] == 20


# --------------------------------------------------------------------------- real external files

from pathlib import Path  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EVF = ROOT / "data" / "external" / "evf"
BCC = ROOT / "data" / "external" / "bcc"
needs_xlsx = pytest.mark.skipif(not (EVF / "raw").exists(), reason="external raw files not present")


@needs_xlsx
def test_raw_files_match_manifest():
    from argus.external.manifest import check_files

    res = check_files(ROOT / "data" / "external")
    committed = [f for f in res if f["committed"]]
    assert committed and all(f["ok"] for f in committed), res
    # files fetched on demand must match when present
    assert all(f["ok"] for f in res if f["present"]), res


@needs_xlsx
def test_evf_every_series_is_mapped_and_points_are_usable():
    pytest.importorskip("openpyxl")
    from argus.external.sources import evf
    from argus.ml.features import eligible

    recs = list(evf.records(EVF))  # raises if a series is unmapped
    rows = enrich_external(recs)
    assert len(recs) == 137 and len({r.paper_key for r in recs}) == 14
    assert all(eligible(r) for r in rows)
    assert all(r["phi_basis"] == "reported" and r["k_matrix_basis"] == "reported" for r in rows)
    # each included series' Vf = 0 point equals its matrix k within 2 %
    assert all(abs(z["rel_diff"]) < 0.02 for z in evf.zero_loading_check(EVF))


@needs_xlsx
def test_evf_map_rejects_unmapped_series(tmp_path):
    pytest.importorskip("openpyxl")
    import shutil

    from argus.external.sources import evf

    (tmp_path / "raw").mkdir()
    shutil.copy(EVF / evf.WORKBOOK, tmp_path / evf.WORKBOOK)
    (tmp_path / "series_map.yaml").write_text("include: {}\nexclude: {SiO2_Epoxy_20um: x}\n", encoding="utf-8")
    with pytest.raises(evf.MappingError, match="unmapped"):
        list(evf.records(tmp_path))


@needs_xlsx
def test_emt_matches_evf_implementation_exactly():
    pytest.importorskip("openpyxl")
    from argus.external.physics_check import check_evf

    res = check_evf(EVF)
    for m in ("maxwell", "bruggeman", "hill", "nan"):
        assert res[m]["n"] == 137 and res[m]["n_exact"] == 137, (m, res[m])


@needs_xlsx
def test_emt_matches_bcc_implementation():
    pytest.importorskip("openpyxl")
    from argus.external.physics_check import check_bcc

    res = check_bcc(BCC)
    assert res["maxwell_garnett"]["n_exact"] == res["maxwell_garnett"]["n"] == 242
    assert res["hasselman_johnson"]["n_exact"] == res["hasselman_johnson"]["n"] == 242
    dem = res["bruggeman_dem"]
    assert dem["n_close"] >= 170
    # every disagreement is on their side: our root solves the DEM equation, theirs does not
    assert dem["max_abs_residual_ours"] < 1e-10 < dem["min_abs_residual_theirs"]


def test_crosscheck_keeps_only_closer_direction_for_unknown_argus_row():
    argus = [_argus("a1", "10.1/a", 15, 6.07)]  # direction unknown
    ext = enrich_external([_rec(ext_id="ip", vol_pct=15, k=6.54, direction="in-plane"),
                           _rec(ext_id="tp", vol_pct=15, k=0.7, direction="through-plane")])
    res = crosscheck(ext, argus)
    assert [p["ext_row"] for p in res["pair_rows"]] == ["t-ip"]
    assert [u["ext_row"] for u in res["unmatched_external"]] == ["t-tp"]
    assert res["grades"] == {"minor": 1}


def test_crosscheck_compares_on_wt_when_both_report_wt():
    argus = [dict(_argus("a1", "10.1/a", None, 6.83), filler_loading_wt_pct=75.0, filler_loading_vol_pct="")]
    ext = enrich_external([_rec(ext_id="1", vol_pct=None, wt_pct=75.0, k=6.9, filler="AlN"),
                           _rec(ext_id="2", vol_pct=None, wt_pct=80.0, k=6.86, filler="AlN")])
    argus[0]["filler_material"] = "AlN"
    res = crosscheck(ext, argus)
    assert [(p["ext_row"], p["loading_basis"]) for p in res["pair_rows"]] == [("t-1", "wt")]
    assert [u["ext_row"] for u in res["unmatched_external"]] == ["t-2"]


def test_tagp_and_heliyon_adapters():
    from argus.external.sources import heliyon, tagp

    t = enrich_external(tagp.records(ROOT / "data" / "external" / "tagp"))
    assert len(t) == 21  # DS03: 12 non-zero points, DS04: 9
    assert {r["doi"] for r in t} == {"10.1021/acsami.8b16616", "10.1002/adfm.201900412"}
    assert all(r["k_matrix_basis"] == "reported" for r in t)
    assert {r["direction_reported"] for r in t if r["doi"] == "10.1002/adfm.201900412"} == {"in-plane"}
    h = enrich_external(heliyon.records(ROOT / "data" / "external" / "heliyon"))
    assert len(h) == 4 and {r["direction_reported"] for r in h} == {"in-plane", "through-plane"}


NC = ROOT / "data" / "external" / "ncomms"


@pytest.mark.skipif(not (NC / "raw").exists(), reason="ncomms workbook not fetched (licence: fetched on demand)")
def test_ncomms_block_map_tiles_the_workbook():
    pytest.importorskip("openpyxl")
    from argus.external.sources import ncomms
    from argus.ml.features import eligible

    rows = enrich_external(ncomms.records(NC))  # check_map raises on any gap or label mismatch
    assert len(rows) == 138 and all(eligible(r) for r in rows)
    assert "UNSPECIFIED" not in {r["method_class"] for r in rows}


def test_new_method_abbreviations_classified():
    from argus.vocab import classify_method

    assert classify_method("THW, ASTM C1113").method_class == "HOT_WIRE"
    assert classify_method("TPS, 2500S").method_class == "TPS"
    assert classify_method("HFM, ASTM C518").method_class == "SS_HFM_GHP"
    assert classify_method("GHP, DRL-III").method_class == "SS_HFM_GHP"
    assert classify_method("MTPS sensor").method_class != "TPS"
