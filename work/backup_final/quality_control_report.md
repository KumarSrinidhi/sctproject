# Quality Control Report

**Dataset:** `thermal_conductivity_dataset.csv`
**Generated:** 2026-10-13 (Phase 2 remediation 2026-10-14; Phase 3 expansion 2026-10-14; Phase 4 merge + **finalized 2026-10-18**)
**Scope:** Experimental effective thermal conductivity of polymer–ceramic composites (epoxy + h-BN/BNNS/AlN primary; other matrices and fillers tagged in notes).
**Final presentation summary:** see `FINAL_REPORT.md`. Final verification: `work/final_verification.json` (14/14 PASS).

---

## 1. Summary statistics (final: 260 rows / 95 papers)

| Metric | Value |
|---|---|
| Total rows | 260 |
| Unique papers | 95 |
| Year range | 1997–2026 |
| k_composite range | 0.17 – 47.03 W/m·K |
| Median k | 1.05 W/m·K |

### By matrix polymer
| Matrix | Rows |
|---|---|
| Epoxy-based | 230 |
| Silicone | 14 |
| Polyimide | 9 |
| PDMS | 2 |
| PEG PCM | 2 |
| Polystyrene | 2 |
| Polyurethane | 1 |

### By filler material
| Filler | Rows |
|---|---|
| h-BN | 87 |
| BNNS | 53 |
| BN (unspecified morphology) | 56 |
| AlN | 22 |
| BN/graphene hybrid | 11 |
| Al2O3 | 6 |
| Al2O3/BN hybrid | 5 |
| h-BN/CNT hybrid | 3 |
| Al2O3/BNNS hybrid | 2 |
| h-BN/Al2O3 hybrid | 2 |
| BNNS/diamond hybrid | 2 |
| MgO | 2 |
| none | 2 |
| cBN | 2 |
| Cu/BN hybrid · BNNS hybrid · AlN/BN hybrid · Al2O3/graphene hybrid · BNNS/SiC hybrid | 1 each |

### By confidence
| Confidence | Rows |
|---|---|
| High | 196 (75.4%) |
| Medium | 64 (24.6%) |

### By value source
| Source | Rows |
|---|---|
| Text | 160 |
| Table | 72 |
| Figure (pixel-digitized, Phase 4) | 28 |

---

## 2. Validation checks

- **k_composite_W_mK:** all 260 values numeric, positive, in range 0.17–47.03 (no zeros, no negatives, no NaN).
- **k_original_value + k_original_unit:** present for all rows.
- **filler_loading:** vol_pct, wt_pct, or original_value present for 259/260 rows (validation rule: at least one; 0.0 wt% neat-resin baselines count as present); one documented exception `bf4f3fd7-182` whose loading is the BN/PA66 sample designation `30-4` (not wt%) — string relocated to `notes` in Phase 2, no numeric loading exists for this scaffold sample.
- **source_location:** present for all rows (traceable to text/table/figure in source).
- **doi + paper_title:** present for all rows (merged from paper_meta).
- **confidence:** High or Medium for all rows (no Low in final dataset).
- **unit normalization:** `normalize_k()` applied; original units preserved in `k_original_unit`.
- **Final re-verification (2026-10-18, after Phase 4):** JSONL↔CSV field-identical, 260 unique row_ids, none of the 15 Phase-2 dropped IDs resurrected, `uncertain_measurements.csv` covers all 64 Medium rows, inventory = 95 papers; Phase-4 checks: all 28 figure rows Medium and traceable to digitizer + overlay, 4 upgraded rows High with full-text `source_location`, Ag-hybrid value still excluded, figure-only DOIs re-classified in `unusable_sources.csv` — `work/final_verification.json`.

---

## 3. Uncertain measurements (Medium confidence)

64 rows marked Medium confidence (listed in `uncertain_measurements.csv`): 28 abstract-only Phase-3C rows (4 of the original 32 were upgraded to High in Phase 4) + 28 Phase-4 figure-digitized rows + 8 earlier rows. Typical reasons:
- Figure-digitized values (not text/table): `value_source=figure`; axis resolution ≈0.01–0.02 W/m·K per pixel, error bars not captured.
- Abstract-only: matrix/curing/method metadata incomplete.
- Loading or orientation partly inferred from schematic labels.
- Hybrid filler composition not fully quantified in source text.

These are retained but flagged. Downstream analysis should weight High-confidence rows preferentially.

---

## 4. Rejected / retried extractions

- **extract_018:** 1 row rejected (`non-numeric filler_loading_original_value` for 3D BN/PA66 ratio "30:4"). Retried in extract_018b/018c with numeric placeholder + explanatory notes.
- **extract_015:** TMBPE 6.77 W/mK excluded (loading not stated in text snippet).
- **extract_015:** Pristine BN/ETDS 50 wt% placeholder dropped (figure-only, no absolute k in text).

---

## 5. Excluded sources (with reasons)

See `unusable_sources.csv` for full list (49 entries incl. the Sci-Hub policy row; Phase 3/4 recoveries are kept with their `action` updated). Categories:

| Category | Count | Examples |
|---|---|---|
| Publisher block (403 / captcha) | 37 | Wiley, Elsevier, Springer, IOP, AIP, ACS, SAGE |
| IOP Radware captcha (txt ≠ PDF) | 3 | 10.1088/1361-6528/ac0470, etc. |
| Review article | 1 | 10.3390/ma13163634 |
| Modeling only (no experimental k) | 1 | 10.31248/ajps2025.124 |
| Out of primary scope (carbon / PCM / Si3N4-only) | 4 | 10.3390/ma12091522, molecules28093797, polym13132161, polym17111507 (Si3N4 rows) |
| Figure-only k (no text/table numeric) | 1 (+2 recovered in Phase 4) | polym10030277; polym11071156 and molecules21050670 now pixel-digitized |
| No absolute k in text (relative % only) | 3 | nano9101396, c8ra10645b, ajps2025.124 |

---

## 6. Method coverage

Most rows report standard methods (laser flash, hot disk, guarded heat flow, etc.) without method-specific labels in `measurement_method`. Where the source explicitly named the instrument/method, it is recorded. Temperature is ambient (~25 °C) unless `measurement_temperature_C` is non-empty (e.g., 77 K cryogenic row for polym11081335).

---

## 7. Recommendations for downstream use

1. Filter `confidence == 'High'` for primary analysis (196 rows); additionally exclude `value_source == 'figure'` if only printed numbers are acceptable.
2. Epoxy + BN-family subset (epoxy matrix + h-BN/BN/BNNS/cBN = 169 rows, of which 28 figure-digitized) is the core target scope.
3. Optional matrices (silicone, PI, PDMS, PEG, PS, PU = 30 rows) are tagged; filter out if strictly epoxy-only is needed.
4. Hybrid fillers (Al2O3/BN, AlN/BN, BN+CNT, etc.) are retained with `filler_material` containing "hybrid"; filter by exact filler string if needed.
5. Cross-check `source_location` before citing any single value; figure-derived rows should be independently verified.

---

## 8. Phase 2 remediation (applied 2026-10-14)

Machine-readable record: `work/phase2_applied_changes.json`; backups: `work/backup_phase1/` (restore via `work/phase2_restore.py`).

| Category | Count | Detail |
|---|---|---|
| Rows dropped — intra-paper duplicates | 9 | validation/retry double-append bug |
| Rows dropped — cross-paper duplicates | 5 | `a9d63e6e-014/015/016` (companion-paper pressure series), `a8b6fee9-141/142` (quoted previous work) |
| Rows dropped — out-of-scope | 1 | `4a11b03c-151` literature quote (README exclusion policy) |
| Loading corrections (Table 1 weight basis) | 20 listed / 17 applied | 3 skipped (row dropped); ETL-60→47.1, ETL-70→58.0, EJ-60→53.0, EJ-65→58.2 wt% |
| `paper_title` overwrites | 11 DOIs / 27 surviving dataset rows / 14 log entries | Crossref-verified titles, old titles removed everywhere |
| Sample-label repairs | 3 | `036`→Cu/BN hybrid, `147`→none (0 wt% baseline), `180`→Al2O3/BN hybrid |
| Hybrid-convention labels | 4 (+1 skipped, row dropped) | `095`, `152`, `153`, `188` now contain "hybrid" in `filler_material` |
| Non-numeric cell repairs | 9 | 2 numeric-column (`RT`@094, `55 (AlN)/35 (BN)`@130 → blank + text to notes) + 7 text-column loading strings (→ notes; field set to 31.0/22.0/32.0/empty per audit guidance) |

Dataset: **188 → 173 rows**, 63 papers; confidence 167 High / 6 Medium. `extraction_log.csv` entry `PHASE2-REMEDIATION` appended (rows_appended=0, rows_removed=15); prior 70 entries preserved (titles corrected in-place for the 11 affected DOIs). `unusable_sources.csv` untouched (48 entries).

Open from Phase 1, not addressed here: `normalize_k()` false process claim (D4), unverifiable k=1.052 in row `b639a9c9-159` (D7), 3 silently dropped screened papers (D10), pipeline hardening (Phase 2b).

---

## Phase 3 (RETRY) — source recovery & coverage expansion

Baseline 173 rows / 63 papers → **232 rows / 93 papers** (+59 rows, +30 papers). Both stretch targets met (rows ≥ 200, papers ≥ 65). Verified in `work/phase3_verification.json`: unique row_ids, no resurrection of the 15 dropped Phase-2 row_ids, all k numeric and positive, all rows have `source_location`.

### Routes and outcomes

| Route | Result |
|---|---|
| Phase 3A local re-grep (P064–P066) | +13 rows (RSC `c8ra10645b` Table 1, MDPI `polym10030277`, `nano13152243`) from already-local fulltexts |
| Phase 3B fetch campaign (213 DOIs logged) | 3 new fulltexts (Kobe repository `pc.28534`; MRS-Journal `mrsk.2023.33.12.503`; scichina `ssc-2022-0226`) → +14 rows; 205 blocked; 2 wave-2 failures logged |
| Phase 3C Semantic Scholar abstract harvest | 59 abstracts retrieved, 58 k-patterns; 24 papers / 32 rows extracted (confidence=Medium, `value_source=text`) |

### Scope decisions recorded

- Sci-Hub deliberately NOT used (copyright/piracy policy) — `(policy)` row in `unusable_sources.csv`.
- Carbon-dominant fillers (graphene, CNT, carbon fiber, nanodiamond-core) excluded; ceramic-dominant hybrids included with scope notes (BN/graphene GO-shell P092, BNNS@nanodiamond P088, Al2O3/graphene P066).
- Metal hybrids (Ag P085/P093-Cu) excluded.
- Abstract-only rows: 32 rows flagged Medium confidence with incomplete method/matrix metadata; P087 (HBP-BN, temperature unspecified RT vs 77 K) and P080 (liquid/uncured epoxy matrix) carry explicit notes.
- 3 append-time warnings (non-numeric `filler_loading_original_value` `~1.1` / `44-45`) retained deliberately: original string preserved in `original_value` field, normalized numeric loading in vol/wt columns.

### Known remaining open items

- Full text still unreachable for `pc.29136` (repository DNS), `s10854-024-13657-3` (Springer bot challenge), and ~200 Wiley/Elsevier/IOP/etc. blocked DOIs.
- 3 IOP files in `work/fulltext/` remain captcha HTML.
- Phase-1 items D4, D7, D10 and Phase-2b hardening remain open (not in Phase 3 scope).


---

## Phase 4 — browser full texts + figure digitization (merged 2026-10-18)

Baseline 232 rows / 93 papers → **260 rows / 95 papers**. Change record: `work/phase4_changes.json`; apply script: `work/phase4_apply.py`; pre-state backup: `work/backup_phase4/` (md5-identical to the 232-row audited state).

| Action | Count | Detail |
|---|---|---|
| Medium → High upgrades (full text) | 4 rows / 3 papers | `5.0211580` (AIP OA), `09673911221110143` (SAGE gold OA), `s10854-024-13657-3` ×2 (Springer OA). Added curing agent, filler size, processing, measurement method, k_matrix; `source_location` now quotes the Results section. |
| Publisher-page metadata fixes | 12 field changes / 7 papers | Years corrected (e.g. `app.55612` 2020→2024, `5.0205196` 2023→2024, `ae6b9b` and `slct.202507155` 2025→2026, `5.0211580` 2023→2024); 5 truncated titles completed. |
| Abstract cross-checks (stay Medium) | 6 rows / 5 papers | Publisher abstract pages (`work/phase4_browser/`) confirm every abstract value verbatim; full texts remain paywalled. |
| New figure-digitized rows | 28 rows / 2 papers | `polym11071156` Fig. 11 (15 rows: ETLBN180/30/2 + EJBN30) and `molecules21050670` Fig. 3 (13 rows: GPTMS-treated 10.6 μm and 3.6 μm). `value_source=figure`, `confidence=Medium`. |

### Digitization method and QA

- `work/phase4_digitize_v2.py`: tick-calibrated axes → per-series colour mask → disk opening (removes fitted curves/error bars) → component centroids. Overlays with detected centroids: `work/figures/overlay_*.png`.
- **Calibration check:** digitized x for every ETLBN point lies within 0.1 vol% of the vol% printed in the text (12.9 / 25.7 / 34.2 / 44.7); the assertion is enforced in `phase4_apply.py`.
- Series identity from the figure caption (polym11071156) or in-plot labels (molecules21050670); no legend guessing.
- **Superseded:** the earlier visual estimates in `work/phase4_figures_digitized.json` were NOT used. They listed 3.6 μm points at 10 and 20 vol% that do not exist in Fig. 3 and omitted the ETLBN2 series.
- Occluded markers: 1 point (molecules, 10.6 μm treated at 30 vol%) estimated from visible top edge + median marker half-height; 1 point (ETLBN2-30) partly hidden. Both are flagged in `notes`.

### Deliberately not extracted

- `09673911221110143`: BNNS/Ag hybrid 2.35 W/m·K (metal filler; Phase-3 scope decision retained).
- `5.0211580`: random BNNS/epoxy at 18.34 vol% (stated only relative to another value).
- `pc.29136`: in-plane 2.1 W/m·K (no loading stated; full text paywalled).
- molecules21050670 naked (open-marker) series and polym11071156 x = 0 baselines (overlapping markers).

### Remaining open items

- About 200 publisher-blocked DOIs; 28 Phase-3C rows remain abstract-only (Medium).
- Phase-1 items D4, D7, D10 and Phase-2b hardening are still open.
- Fixed in Phase 4: `build_deliverables.py` used to overwrite the curated `unusable_sources.csv` with its Phase-1 seed list. It now writes that file only when it is missing.
