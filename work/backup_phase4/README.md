# Polymer–Ceramic Thermal Conductivity Dataset

**Source-verified experimental measurements of effective thermal conductivity (k) for polymer–ceramic composites, with primary focus on epoxy + h-BN/BNNS/AlN.**

All values are traceable to a specific paper, table, figure, or text location. No hallucinated or inferred values. Literature-comparison values (Table 1, ref-cited) are excluded.

---

## Deliverables

| File | Contents |
|---|---|
| `thermal_conductivity_dataset.csv` | 232 rows / 93 papers, 31 columns (full schema) |
| `paper_inventory.csv` | 93 papers with row counts, fillers, matrices, k ranges |
| `extraction_log.csv` | Per-batch audit trail (101 entries) with tables/figures inspected |
| `uncertain_measurements.csv` | 40 Medium-confidence rows (32 abstract-only Phase-3C rows + 8 earlier) flagged for review |
| `unusable_sources.csv` | 49 entries: 48 sources excluded with explicit reasons + 1 Sci-Hub policy note |
| `quality_control_report.md` | Validation checks, stats, exclusions, recommendations (incl. Phase 3 section) |
| `FINAL_REPORT.md` | Self-contained presentation-ready summary (key numbers, methodology, QA, figure gallery) |
| `figures/` | 6 final charts generated from the dataset (`work/final_figures.py`) |

---

## Schema (`thermal_conductivity_dataset.csv`)

Key columns:

- `row_id`, `doi`, `source_url`, `paper_title`, `year`
- `matrix_polymer`, `curing_agent`
- `filler_material` (normalized: h-BN / BN / BNNS / AlN / cBN / hybrids), `filler_material_original` (verbatim from source)
- `filler_shape`, `filler_aspect_ratio`, `filler_mean_size_um`, `functionalization`, `filler_alignment`
- `filler_loading_vol_pct`, `filler_loading_wt_pct`, `filler_loading_original_value`, `filler_loading_original_unit`
- `processing_method`
- `k_matrix_W_mK`, `k_composite_W_mK` (normalized to W/m·K), `k_direction`
- `measurement_method`, `measurement_temperature_C`
- `k_original_value`, `k_original_unit` (as printed in source)
- `value_source` (text / table / figure), `source_location` (verbatim quote or table ID)
- `confidence` (High / Medium)
- `notes` (hybrid composition, optional-matrix flags, caveats)

---

## Scope

**Primary (epoxy + BN/AlN):** 202 epoxy-based rows; h-BN (74) + BNNS (53) + BN (41) + AlN (22) = 190 BN/AlN-family rows (Phase 3 counts; see paper_inventory.csv for exact breakdown).

**Optional matrices (tagged in notes):** silicone rubber (14), polyimide (9), PDMS (2), PEG PCM (2), polystyrene (2), polyurethane (1), liquid crystal epoxy (included in epoxy-based count).

**Hybrid fillers retained:** Al2O3/BN, AlN/BN, BN+CNT, h-BN/c-BN, BNNS/MWCNTs@mSiO2, 3D BN/PA66 scaffold, etc. — `filler_material` contains "hybrid"; composition detail in `notes`.

**Excluded:** reviews, modeling-only papers, figure-only k values (no text/table numeric), literature-comparison values, carbon-only fillers, Si3N4-only (non-BN/AlN) matrices, PCM (paraffin/LA-ODE) matrices.

---

## Data characteristics

- **k range:** 0.17 – 47.03 W/m·K (median 0.95; the high tail is in-plane anisotropic BNNS networks at 60 wt%)
- **Year range:** 1997 – 2026
- **Temperature:** ambient (~25 °C) unless `measurement_temperature_C` set (e.g., 77 K cryogenic row)
- **Direction:** `k_direction` = through-plane / in-plane / unknown (as reported)
- **Unit normalization:** all k converted to W/m·K; original units preserved

---

## Extraction methodology

1. **Discovery:** Crossref + Semantic Scholar + Europe PMC API searches (queries targeting polymer/epoxy/BN/AlN/h-BN/BNNS + thermal conductivity).
2. **Triage:** Abstract screening for experimental composite k values.
3. **Full-text retrieval:** Europe PMC fullTextXML (open access), ChemRxiv, unpaywall. Publisher HTML blocked (403) for Wiley/Elsevier/Springer/IOP/ACS — listed in `unusable_sources.csv`. Phase 3 retry added: direct OA repository fetches (Kobe, MRS-Journal, scichina) and Semantic Scholar abstract harvest for still-blocked papers.
4. **Extraction:** Per-paper Python scripts (`work/extract_00N.py` through `extract_027.py`) parse text/tables; each row carries `source_location` (verbatim quote or table ID). Phase-3C rows from abstracts only are `confidence=Medium`, `value_source=text`, with `source_location` prefixed `Abstract (...)`. Validation rejects missing/non-numeric k, loading, source_location.
5. **QC:** `work/io_append.py::append_rows()` enforces schema; rejections logged in `extraction_log.jsonl`.

All extraction scripts, full texts, and logs are in `work/` for reproducibility. Phase-3 change record: `work/phase3_changes.json`; verification: `work/phase3_verification.json`.

---

## How to cite a value

Every row is independently traceable:

```
row_id, doi, source_location
e.g. "bf4f3fd7-042", "10.3390/polym13060955", "Table 2, EP/BN 30 wt%: 0.85 W/(m·K)"
```

Cross-check `source_location` against the paper before using in publication.

---

## Gaps / future work

- ~200 Wiley/Elsevier/Springer/IOP papers still blocked (403 / bot-challenge / captcha) — Phase 3 recovered what OA routes allowed (repositories + Semantic Scholar abstracts); remaining would need browser automation or institutional access.
- 32 Phase-3C rows are abstract-only (`confidence=Medium`) — full text would confirm matrix, curing agent, and measurement method.
- `pc.29136` full text unreachable (repository DNS failure from this host); `s10854-024-13657-3` behind Springer bot challenge.
- Figure-only values (polym11071156, molecules21050670, etc.) could be digitized from PMC figure images.
- IOP captcha-blocked txt replacements (3 files) are unusable; re-fetch via browser if needed.
- Intermediate loadings for some papers not extracted as separate rows (noted in `extraction_log.csv`).

---

## License / provenance

Values extracted from open-access papers (CC-BY, CC-BY-SA, etc.) via Europe PMC fullTextXML. This dataset is for research use; verify against original sources before commercial or regulatory use.
