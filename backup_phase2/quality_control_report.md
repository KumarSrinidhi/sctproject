# Quality Control Report

**Dataset:** `thermal_conductivity_dataset.csv`
**Generated:** 2026-10-13 (Phase 2 remediation applied 2026-10-14)
**Scope:** Experimental effective thermal conductivity of polymer–ceramic composites (epoxy + h-BN/BNNS/AlN primary; other matrices and fillers tagged in notes).

---

## 1. Summary statistics

| Metric | Value |
|---|---|
| Total rows | 173 |
| Unique papers | 63 |
| Year range | 1997–2026 |
| k_composite range | 0.17 – 19.0 W/m·K |
| Median k | 1.03 W/m·K |

### By matrix polymer (top)
| Matrix | Rows |
|---|---|
| Epoxy-based | 143 |
| Silicone | 14 |
| Polyimide | 9 |
| PDMS | 2 |
| PEG PCM | 2 |
| Polystyrene | 2 |
| Polyurethane | 1 |

### By filler material
| Filler | Rows |
|---|---|
| h-BN | 55 |
| BN (unspecified morphology) | 41 |
| BNNS | 37 |
| AlN | 18 |
| Al2O3 | 5 |
| Al2O3/BN hybrid | 5 |
| h-BN/CNT hybrid | 3 |
| Al2O3/BNNS hybrid | 2 |
| none | 2 |
| cBN | 2 |
| Cu/BN hybrid | 1 |
| BNNS hybrid | 1 |
| AlN/BN hybrid | 1 |

### By confidence
| Confidence | Rows |
|---|---|
| High | 167 (96.5%) |
| Medium | 6 (3.5%) |

### By value source
| Source | Rows |
|---|---|
| Text | 121 |
| Table | 52 |

---

## 2. Validation checks

- **k_composite_W_mK:** all 173 values numeric, positive, in range 0.17–19.0 (no zeros, no negatives, no NaN).
- **k_original_value + k_original_unit:** present for all rows.
- **filler_loading:** vol_pct, wt_pct, or original_value present for 172/173 rows (validation rule: at least one); one documented exception `bf4f3fd7-182` whose loading is the BN/PA66 sample designation `30-4` (not wt%) — string relocated to `notes` in Phase 2, no numeric loading exists for this scaffold sample.
- **source_location:** present for all rows (traceable to text/table/figure in source).
- **doi + paper_title:** present for all rows (merged from paper_meta).
- **confidence:** High or Medium for all rows (no Low in final dataset).
- **unit normalization:** `normalize_k()` applied; original units preserved in `k_original_unit`.

---

## 3. Uncertain measurements (Medium confidence)

6 rows marked Medium confidence (listed in `uncertain_measurements.csv`). Typical reasons:
- Figure-digitized values (not text/table).
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

See `unusable_sources.csv` for full list (48 entries). Categories:

| Category | Count | Examples |
|---|---|---|
| Publisher block (403 / captcha) | 37 | Wiley, Elsevier, Springer, IOP, AIP, ACS, SAGE |
| IOP Radware captcha (txt ≠ PDF) | 3 | 10.1088/1361-6528/ac0470, etc. |
| Review article | 1 | 10.3390/ma13163634 |
| Modeling only (no experimental k) | 1 | 10.31248/ajps2025.124 |
| Out of primary scope (carbon / PCM / Si3N4-only) | 4 | 10.3390/ma12091522, molecules28093797, polym13132161, polym17111507 (Si3N4 rows) |
| Figure-only k (no text/table numeric) | 3 | polym11071156, molecules21050670, polym10030277 |
| No absolute k in text (relative % only) | 3 | nano9101396, c8ra10645b, ajps2025.124 |

---

## 6. Method coverage

Most rows report standard methods (laser flash, hot disk, guarded heat flow, etc.) without method-specific labels in `measurement_method`. Where the source explicitly named the instrument/method, it is recorded. Temperature is ambient (~25 °C) unless `measurement_temperature_C` is non-empty (e.g., 77 K cryogenic row for polym11081335).

---

## 7. Recommendations for downstream use

1. Filter `confidence == 'High'` for primary analysis (167 rows).
2. Epoxy + BN-family subset (h-BN + BN + BNNS = 133 rows) is the core target scope.
3. Optional matrices (silicone, PI, PDMS, PEG, PS, PU, LC epoxy = 30 rows) are tagged; filter out if strictly epoxy-only is needed.
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

Open from Phase 1, not addressed here: `normalize_k()` false process claim (D4), unverifiable k=1.052 in row `b639a9c9-159` (D7), 3 silently dropped screened papers (D10), pipeline hardening (Phase 2b). Phase 3 (source recovery / coverage expansion) not started.
