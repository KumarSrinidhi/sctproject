"""Phase 4 merge: full-text upgrades, publisher-page metadata fixes, figure-digitized rows.

Run from the project root:  python work/phase4_apply.py
Pre-state snapshot: work/backup_phase4/ (md5-identical to the 232-row audited final).
Idempotent: refuses to run if any Phase-4 row/change is already present.

Inputs
  work/fulltext/10.1063_5.0211580.txt          AIP OA full HTML (browser-fetched)
  work/fulltext/10.1177_09673911221110143.txt  SAGE gold-OA full HTML (browser-fetched)
  work/fulltext/10.1007_s10854-024-13657-3.txt Springer OA full HTML
  work/phase4_browser/*.txt                    publisher abstract pages (paywalled; abstract only)
  work/phase4_figures_digitized_v2.json        pixel digitization (work/phase4_digitize_v2.py)
Outputs
  work/rows_raw.jsonl, work/extraction_log.jsonl (updated), work/phase4_changes.json,
  unusable_sources.csv (curated; updated in place AFTER build_deliverables.py, which would
  otherwise overwrite it with its stale hard-coded list).
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
W = ROOT / "work"
sys.path.insert(0, str(W))
from io_append import append_rows  # noqa: E402

ROWS = W / "rows_raw.jsonl"
LOG = W / "extraction_log.jsonl"
DATE = "2026-10-18"

rows = [json.loads(l) for l in open(ROWS, encoding="utf-8")]
by_id = {r["row_id"]: r for r in rows}
if any(r["doi"] in ("10.3390/polym11071156", "10.3390/molecules21050670") for r in rows):
    sys.exit("Phase 4 already applied (figure-digitized DOIs present); restore work/backup_phase4 first.")

changes = {"phase": "4 (browser full texts + figure digitization)", "date": DATE,
           "baseline": {"rows": len(rows), "papers": len({r["doi"] for r in rows})},
           "upgrades": [], "metadata_corrections": [], "abstract_crosschecks": [], "new_rows": [],
           "not_extracted": [], "superseded": []}

# ---------------------------------------------------------------- 1. full-text upgrades
FT = "Full text ({src}; work/fulltext/{f})"
UPGRADES = {
    "fd88f33b-209": dict(
        matrix_polymer="Epoxy (dielectric)",
        filler_alignment="Vertically aligned (directional freeze-cast ANF-BNNS framework)",
        processing_method="ANF-BNNS aerogel by directional freezing + vacuum freeze-drying; vacuum infusion/impregnation with epoxy",
        k_matrix_W_mK=0.184,
        measurement_method="Not stated in main text (characterization in supplementary material)",
        source_location=FT.format(src="AIP OA HTML", f="10.1063_5.0211580.txt") +
        ", Sec. III: \"The through-plane λ of ANF-BNNS/epoxy reaches up to 0.87 W m−1 K−1 at only 1.43 vol. % BNNS, "
        "a value of 372.8% greater than that of pure epoxy (∼0.184 W m−1 K−1)\"",
        notes="Upgraded Phase 4 (full text). Loading = BNNS fraction. The BNNS/epoxy random comparator "
              "(30 wt%/18.34 vol%) is only given relative to this value (\"~17.1% higher\"), so no row was derived for it.",
    ),
    "b1ee3c22-222": dict(
        matrix_polymer="DGEBA epoxy (epoxy equivalent 185)",
        curing_agent="2-ethyl-4-methylimidazole (2E4MI)",
        filler_material_original="BNNSs only (liquid-phase exfoliated; baseline in same paper; silver-linked hybrid excluded as metal-containing)",
        filler_mean_size_um=3.0, filler_aspect_ratio=600.0,
        size_distribution="lateral ~3 μm, thickness ~5 nm (AFM/TEM)",
        processing_method="BNNS exfoliated in DMF (48 h sonication); mixed with DGEBA + 2E4MI; vacuum degassed at 80 °C; cured 150 °C, 8 h",
        k_matrix_W_mK=0.21,
        measurement_method="Laser flash (Netzsch LFA467 HyperFlash, ASTM E1461-13), room temperature",
        source_location=FT.format(src="SAGE gold-OA HTML", f="10.1177_09673911221110143.txt") +
        ", Results (Thermal conductivity...): \"The pure epoxy has a poor λ of 0.21 W/mK... When the Vf reaches up to 20%, "
        "the λ of the composites filled with BNNSs/[Ag (2E4MI)2]Ac hybrids reaches 2.35 W/mK, but that for BNNSs alone is only 1.26 W/mK.\"",
        notes="Upgraded Phase 4 (full text). Silver-bridged hybrid value (2.35 W/mK) still NOT extracted: silver is a metal, "
              "outside ceramic-filler scope (Phase 3 decision retained). Aspect ratio 600 = L/H as stated in paper.",
    ),
    "7dee9c50-202": dict(
        matrix_polymer="Bisphenol A-type epoxy (CYD-128)",
        curing_agent="Methyl tetrahydrophthalic anhydride + 2,4,6-tris(dimethylaminomethyl)phenol (100:81:1)",
        filler_mean_size_um=10.0,
        processing_method="BN ultrasonically dispersed in ethanol; epoxy mixed at 60 °C; anhydride + accelerator; degassed; cured 60 °C then 80/120/150 °C, 1 h each",
        measurement_method="Laser flash (NETZSCH LFA447), room temperature",
        source_location=FT.format(src="Springer OA HTML", f="10.1007_s10854-024-13657-3.txt") +
        ", Sec. 3: \"The heat conduction of the BN/Ep reaches 0.817 W/(mK) at BN content of 30 wt%\"",
        notes="Upgraded Phase 4 (full text). 10 and 20 wt% values are figure-only (Fig. 3b), not extracted.",
    ),
    "7dee9c50-203": dict(
        matrix_polymer="Bisphenol A-type epoxy (CYD-128)",
        curing_agent="Methyl tetrahydrophthalic anhydride + 2,4,6-tris(dimethylaminomethyl)phenol (100:81:1)",
        filler_mean_size_um=10.0,
        processing_method="BN-PCPA-Si69 ultrasonically dispersed in ethanol; epoxy mixed at 60 °C; anhydride + accelerator; degassed; cured 60 °C then 80/120/150 °C, 1 h each",
        measurement_method="Laser flash (NETZSCH LFA447), room temperature",
        source_location=FT.format(src="Springer OA HTML", f="10.1007_s10854-024-13657-3.txt") +
        ", Sec. 3: \"that of mBN/Ep at the same content reaches 0.881 W/(mK). In comparison to pure epoxy resin (0.200 W/(m·K))\"",
        notes="Upgraded Phase 4 (full text). Paper is internally inconsistent: Conclusions give 0.879 W/m·K for mBN30/Ep; "
              "Results/abstract value 0.881 kept. 0.881/0.200-1 = 340% vs stated 364%.",
    ),
}
for rid, upd in UPGRADES.items():
    r = by_id[rid]
    before = {k: r.get(k, "") for k in list(upd) + ["confidence"]}
    r.update(upd)
    r["confidence"] = "High"
    changes["upgrades"].append({"row_id": rid, "doi": r["doi"], "confidence": "Medium -> High",
                                "fields_changed": sorted(k for k in upd if before.get(k) != upd[k]),
                                "before": before})

# ---------------------------------------------------------------- 2. metadata corrections (publisher pages)
META = {
    "10.1063/5.0211580": dict(year=2024, paper_title="Significantly enhancing the through-plane thermal conductivity of epoxy "
                              "dielectrics by constructing aramid nanofiber/boron nitride three-dimensional interconnected framework"),
    "10.1177/09673911221110143": dict(paper_title="Improved thermal conductivity of epoxy composites via linked boron nitride "
                                      "nanosheets with in-situ generated silver nanoparticles"),
    "10.1007/s10854-024-13657-3": dict(paper_title="Functionalization of boron nitride with poly(catechol-polyamine) and "
                                       "bis(γ-triethoxysilylpropyl)tetrasulfide for preparing epoxy nanocomposites with enhanced thermal conductivity"),
    "10.1002/app.55612": dict(year=2024, paper_title="Sugar-template method to construct a boron nitride filler network to "
                              "enhance the thermal conductivity of epoxy composites"),
    "10.1063/5.0205196": dict(year=2024),
    "10.1088/1361-6463/ae6b9b": dict(year=2026, paper_title="Interface engineering of AlN via phosphoric acid modification for "
                                     "enhanced thermal conduction, electrical insulation, and mechanical properties of epoxy composites"),
    "10.1002/slct.202507155": dict(year=2026),
}
EVIDENCE = {
    "10.1063/5.0211580": "AIP article page: J. Appl. Phys. 136, 045101 (2024), July 22 2024",
    "10.1177/09673911221110143": "SAGE article page title",
    "10.1007/s10854-024-13657-3": "Springer article page title; J Mater Sci: Mater Electron 35, 1906 (2024)",
    "10.1002/app.55612": "Wiley page: J. Appl. Polym. Sci. 141(27) e55612, first published 24 April 2024",
    "10.1063/5.0205196": "AIP page: J. Chem. Phys. 160, 154903 (2024)",
    "10.1088/1361-6463/ae6b9b": "IOP page: J. Phys. D 59 205502 (2026), published 22 May 2026",
    "10.1002/slct.202507155": "Wiley page: ChemistrySelect 11(12) e07155, first published 19 March 2026",
}
for doi, upd in META.items():
    for r in rows:
        if r["doi"] != doi:
            continue
        for k, v in upd.items():
            if r[k] != v:
                changes["metadata_corrections"].append({"row_id": r["row_id"], "doi": doi, "field": k,
                                                        "before": r[k], "after": v, "evidence": EVIDENCE[doi]})
                r[k] = v

# ---------------------------------------------------------------- 3. abstract cross-checks (still Medium)
CROSS = {
    "10.1002/pc.29136": "Wiley abstract page; full text paywalled. In-plane value (\"to 2.1 W/mK\") has no stated loading -> not extracted.",
    "10.1002/slct.202507155": "Wiley abstract page; full text paywalled.",
    "10.1063/5.0205196": "AIP abstract page (Cloudflare cleared in browser); full text paywalled.",
    "10.1088/1361-6463/ae6b9b": "IOP abstract page; full text paywalled.",
    "10.1002/app.55612": "Wiley abstract page; full text paywalled.",
}
for doi, why in CROSS.items():
    for r in rows:
        if r["doi"] == doi:
            r["notes"] = (r["notes"] + " " if r["notes"] else "") + \
                f"Phase 4: value re-confirmed against publisher abstract page (work/phase4_browser/); {why}"
            changes["abstract_crosschecks"].append({"row_id": r["row_id"], "doi": doi, "k": r["k_composite_W_mK"],
                                                    "result": "value confirmed verbatim", "detail": why})

with open(ROWS, "w", encoding="utf-8") as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

with open(LOG, "a", encoding="utf-8") as f:
    f.write(json.dumps({
        "candidate_id": "P4-UPG", "doi": "; ".join(sorted({c["doi"] for c in changes["upgrades"]})),
        "paper_title": "Phase 4 full-text upgrades of Phase-3C abstract-only rows", "date_processed": DATE,
        "access_result": "Full text via browser (AIP OA, SAGE gold-OA) and Springer OA HTML",
        "files_inspected": "work/fulltext/10.1063_5.0211580.txt; work/fulltext/10.1177_09673911221110143.txt; "
                           "work/fulltext/10.1007_s10854-024-13657-3.txt",
        "tables_inspected": "SAGE Table 1 (XPS composition; no k)", "figures_inspected": "captions only",
        "candidate_measurements": 4, "rows_appended": 0,
        "unit_conversions": "none (W/mK as printed)",
        "duplicate_checks": "in-place upgrade of existing row_ids; no new rows",
        "qc_findings": "4 rows Medium->High; s10854 Results 0.881 vs Conclusions 0.879 noted; Ag-hybrid exclusion retained",
        "rows_rejected_at_append": [],
    }, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- 4. figure-digitized rows
dig = json.load(open(W / "phase4_figures_digitized_v2.json", encoding="utf-8"))
DIGI = "pixel-digitized with work/phase4_digitize_v2.py (overlay: work/figures/overlay_{img})"


def fig_row(**kw):
    base = dict(value_source="figure", confidence="Medium", k_direction="unknown", k_original_unit="W/mK")
    base.update(kw)
    return base


# --- polym11071156 (Polymers 2019, Fig. 11)
P = dig["10.3390/polym11071156"]
img = "polymers-11-01156-g011.png"
TEXT_VOL = {30: 12.9, 50: 25.7, 60: 34.2, 70: 44.7}   # text: "ETLBNx-30, 12.9; -50, 25.7; -60, 34.2 vol%", "44.7 vol%"
ETL = dict(matrix_polymer="DGEBA epoxy (Araldite GY240), thiol-cured",
           curing_agent="Pentaerythritol tetrakis(3-mercaptopropionate) thiol (~60:40 epoxy:thiol) + LC-80 encapsulated imidazole initiator (2 phr)")
EJ = dict(matrix_polymer="DGEBA epoxy (Araldite GY240), diamine-cured",
          curing_agent="Jeffamine D-420 diamine")
COMMON_P = dict(filler_material="BN", filler_shape="platelet", functionalization="None (no surface treatment or coupling agent)",
                processing_method="Hand-mixed, cast in silicone mould, vacuum degassed at RT, cured isothermally 70 °C 1 h",
                measurement_method="Transient Hot Bridge (Linseis THB-100, Kapton Hot Point sensor), surfaces polished")
p_rows = []
for series, size, mat in [("ETLBN180 (purple diamonds)", 180, ETL), ("ETLBN30 (orange triangles)", 30, ETL),
                          ("ETLBN2 (blue circles)", 2, ETL)]:
    pts = P["series"][series]
    for pt, y in zip(pts, [30, 50, 60, 70]):
        vol = TEXT_VOL[y]
        assert abs(pt["x"] - vol) < 0.5, (series, pt, vol)   # digitized x must match the printed vol%
        note = (f"Figure-only value; digitized x={pt['x']} vs printed {vol} vol% (calibration check). "
                f"wt% w.r.t. epoxy+BN (Table 1). Axis resolution ~{P['resolution']['k_W_mK_per_px']} W/mK per px.")
        if pt["area_px"] < 80:
            note += f" Marker partly hidden under neighbouring marker (area {pt['area_px']} px); k may be biased by up to ~0.05 W/mK."
        if size == 2:
            note += " 44.7 vol% not achievable for 2 μm platelets (paper text)."
        p_rows.append(fig_row(**COMMON_P, **mat,
                              filler_material_original=f"BN platelets, {size} μm (Saint-Gobain), sample ETLBN{size}-{y}",
                              filler_mean_size_um=float(size),
                              filler_loading_vol_pct=vol, filler_loading_wt_pct=float(y),
                              filler_loading_original_value=vol, filler_loading_original_unit="vol%",
                              k_composite_W_mK=round(pt["k"], 2), k_original_value=round(pt["k"], 2),
                              source_location=f"Figure 11, {series}, ETLBN{size}-{y} at {vol} vol%; " + DIGI.format(img=img),
                              notes=note))
for pt in [p for p in P["series"]["EJBN30 (grey squares)"] if p["x"] > 1]:
    vol = round(pt["x"], 1)
    p_rows.append(fig_row(**COMMON_P, **EJ,
                          filler_material_original="BN platelets, 30 μm (Saint-Gobain), EJBN30 series (diamine-cured comparator)",
                          filler_mean_size_um=30.0,
                          filler_loading_vol_pct=vol, filler_loading_original_value=vol, filler_loading_original_unit="vol% (digitized x)",
                          k_composite_W_mK=round(pt["k"], 2), k_original_value=round(pt["k"], 2),
                          source_location=f"Figure 11, EJBN30 (grey squares) at x≈{vol} vol%; " + DIGI.format(img=img),
                          notes="Figure-only value. Loading is the digitized x position (vol% not printed for EJBN30; "
                                f"±{P['resolution']['x_units_per_px']} vol% per px). Per-point sample designation not stated."))

# --- molecules21050670 (Molecules 2016, Fig. 3)
M = dig["10.3390/molecules21050670"]
img = "molecules-21-00670-g003.png"
COMMON_M = dict(matrix_polymer="Cresol novolac epoxy (CNE200EL)",
                curing_agent="Phenol novolac hardener (PF1120HH) + 1-benzyl-2-methylimidazole catalyst",
                filler_material="h-BN", filler_shape="particle",
                functionalization="GPTMS silane surface treatment",
                processing_method="Dry mixing (≤40 vol%) or acetone solvent mixing (>40 vol%); moulded 175 °C, 50 kg/cm², 5 min; post-cured 180 °C 6 h",
                measurement_method="Laser flash (Netzsch LFA447); K = Cp·ρ·α")
m_rows = []
for series, size in [("treated 10.6um (filled green squares)", 10.6), ("treated 3.6um (filled blue circles)", 3.6)]:
    for pt in M["series"][series]:
        vol = float(round(pt["x"] / 10) * 10)
        assert abs(pt["x"] - vol) < 0.5, (series, pt)
        note = (f"Figure-only value; digitized x={pt['x']} (nominal {vol:g} vol%). "
                f"Axis resolution ~{M['resolution']['k_W_mK_per_px']} W/mK per px. Error bars in figure not captured. "
                "GPTMS optimum per Fig. 2: 2.4 wt% (10.6 μm) / 3.6 wt% (3.6 μm).")
        if "occluded" in pt:
            note += " Marker partly hidden; " + pt["occluded"] + "."
        if size == 3.6 and vol == 30:
            note += " Treated 3.6 μm series has no visible point at 40 vol% (not extracted)."
        m_rows.append(fig_row(**COMMON_M,
                              filler_material_original=f"Combustion-synthesized h-BN, d50 = {size} μm, GPTMS-treated",
                              filler_mean_size_um=size, size_distribution=f"d50 = {size} μm",
                              filler_loading_vol_pct=vol, filler_loading_original_value=vol, filler_loading_original_unit="vol%",
                              k_composite_W_mK=round(pt["k"], 2), k_original_value=round(pt["k"], 2),
                              source_location=f"Figure 3, {series} at {vol:g} vol%; " + DIGI.format(img=img),
                              notes=note))

FIGLOG = dict(date_processed=DATE, access_result="Europe PMC full text (OA, CC-BY) + figure image from PMC CDN (browser-fetched)",
              tables_inspected="Table 1 (composition)", unit_conversions="none (axis label W/mK)",
              duplicate_checks="new DOI; no prior rows")
n1, _ = append_rows(dict(doi="10.3390/polym11071156", source_url="https://doi.org/10.3390/polym11071156",
                         paper_title="Achieving High Thermal Conductivity in Epoxy Composites: Effect of Boron Nitride Particle Size and Matrix-Filler Interface",
                         year=2019), p_rows,
                    dict(FIGLOG, candidate_id="P4-FIG1", doi="10.3390/polym11071156",
                         paper_title="Achieving High Thermal Conductivity in Epoxy Composites: Effect of Boron Nitride Particle Size and Matrix-Filler Interface",
                         files_inspected="work/fulltext/10.3390_polym11071156.txt; work/figures/polymers-11-01156-g011.jpg",
                         figures_inspected="Fig. 11 (4 series; caption identifies series by marker)",
                         candidate_measurements=len(p_rows),
                         qc_findings="Digitized ETLBN x within 0.5 of printed vol% for all points; x=0 baselines overlap (k_matrix not set); "
                                     "earlier visual digitization (phase4_figures_digitized.json) superseded"))
n2, _ = append_rows(dict(doi="10.3390/molecules21050670", source_url="https://doi.org/10.3390/molecules21050670",
                         paper_title="Thermal Conductivity of Epoxy Resin Composites Filled with Combustion Synthesized h-BN Particles",
                         year=2016), m_rows,
                    dict(FIGLOG, candidate_id="P4-FIG2", doi="10.3390/molecules21050670",
                         paper_title="Thermal Conductivity of Epoxy Resin Composites Filled with Combustion Synthesized h-BN Particles",
                         files_inspected="work/fulltext/10.3390_molecules21050670.txt; work/figures/molecules-21-00670-g003.jpg",
                         figures_inspected="Fig. 3 (treated series digitized; naked/open-marker series not digitized)",
                         candidate_measurements=len(m_rows),
                         qc_findings="Earlier visual digitization listed 3.6 um points at 10/20 vol% that do not exist in the figure; "
                                     "superseded by pixel digitization"))

new = [json.loads(l) for l in open(ROWS, encoding="utf-8")][len(rows):]
changes["new_rows"] = [{"row_id": r["row_id"], "doi": r["doi"], "loading": r["filler_loading_original_value"],
                        "k": r["k_composite_W_mK"], "source_location": r["source_location"]} for r in new]
changes["not_extracted"] = [
    {"doi": "10.1177/09673911221110143", "value": "2.35 W/mK (BNNS/[Ag(2E4MI)2]Ac, 20 vol%)", "reason": "metal (Ag) hybrid; out of ceramic-filler scope"},
    {"doi": "10.1063/5.0211580", "value": "BNNS/epoxy random, 18.34 vol%", "reason": "only stated relative to another value; would require derivation"},
    {"doi": "10.1002/pc.29136", "value": "in-plane 2.1 W/mK", "reason": "no loading stated in abstract; full text paywalled"},
    {"doi": "10.3390/molecules21050670", "value": "naked (untreated) series, open markers", "reason": "hollow markers not reliably separable by colour mask from curves/error bars"},
    {"doi": "10.3390/polym11071156", "value": "x=0 neat ETL/EJ baselines", "reason": "overlapping markers; series not separable"},
]
changes["superseded"] = [{"file": "work/phase4_figures_digitized.json",
                          "reason": "visual estimates; molecules21050670 3.6 um series listed points at 10/20 vol% that are absent from Fig. 3 "
                                    "and polym11071156 omitted the ETLBN2 series. Replaced by work/phase4_figures_digitized_v2.json."}]
changes["after"] = {"rows": len(rows) + n1 + n2, "papers": len({r["doi"] for r in rows} | {r["doi"] for r in new})}

# ---------------------------------------------------------------- 5. rebuild deliverables, then curated unusable_sources.csv
subprocess.run([sys.executable, str(W / "build_deliverables.py")], cwd=ROOT, check=True)
(ROOT / "unusable_sources.csv").write_bytes((W / "backup_phase4" / "unusable_sources.csv").read_bytes())
UNUSABLE = {
    "10.3390/polym11071156": ("Figure-only k values (no text numeric)",
                              "recovered (Phase 4 pixel digitization of Fig. 11; value_source=figure, Medium confidence)"),
    "10.3390/molecules21050670": ("Own data figure-only; text values are literature comparisons",
                                  "recovered (Phase 4 pixel digitization of Fig. 3; value_source=figure, Medium confidence)"),
}
for doi in ("10.1002/slct.202507155", "10.1088/1361-6463/ae6b9b", "10.1063/5.0205196"):
    UNUSABLE[doi] = (None, None)
with open(ROOT / "unusable_sources.csv", encoding="utf-8-sig") as f:
    un = list(csv.DictReader(f))
for u in un:
    if u["doi"] in UNUSABLE:
        reason, action = UNUSABLE[u["doi"]]
        if reason is None:
            u["reason"] += "; Phase 4: publisher abstract page re-checked in browser, full text still paywalled"
        else:
            u["reason"], u["action"] = reason, action
with open(ROOT / "unusable_sources.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["doi", "reason", "action"])
    w.writeheader()
    w.writerows(un)

json.dump(changes, open(W / "phase4_changes.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"upgrades={len(changes['upgrades'])} metadata={len(changes['metadata_corrections'])} "
      f"crosschecks={len(changes['abstract_crosschecks'])} new_rows={n1 + n2} -> {changes['after']}")
