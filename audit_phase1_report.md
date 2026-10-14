# ARGUS Thermal-Conductivity Dataset — Phase 1 Zero-Trust Audit Report

**Date:** 2026-10-14
**Target:** `C:\Users\Ivermectin\Desktop\sctproject` (ARGUS polymer–ceramic thermal-conductivity dataset)
**Mode:** READ-ONLY audit — no existing artifact was modified; only new files were created (listed in §13)
**Environment:** Windows (win32), Python 3.13.13, PowerShell (cp1252; `PYTHONIOENCODING=utf-8` used for all runs)
**Version control:** NOT a git repository (`git rev-parse` → exit 128); byte-preservation of deliverables verified via SHA-256 recorded at start and end of audit (identical)

---

## 1. Executive summary

The deliverables are **structurally sound and their headline claims reproduce exactly**: 188 rows, 31 columns, 63 DOIs, 179 High / 9 Medium confidence, k = 0.17–19.0 W/m·K (median 1.052), 70 extraction-log entries, 48 unusable sources, year range 1997–2026, text/table split 131/57 — all re-computed from the files and all match. Extraction-log DOIs and dataset DOIs are identical sets (zero drift), and `work/rows_raw.jsonl` matches the deliverable CSV.

Underneath the clean structure, the audit found **real defects that must be fixed before publication-grade use**:

- **9 intra-paper duplicate pairs** caused by a validation bug that *logs rows as "rejected" but appends them anyway*; retry scripts then re-append the same measurement → **188 rows contain only 179 unique measurements**.
- **20 rows mislabel loading**: `filler_loading_wt_pct` stores formulation *parts* (paper's own "70% by weight of BN w.r.t. combined epoxy+BN") where the paper's actual composition is **58.0 wt%** (the paper itself says so). The vol% column is correct.
- **5 cross-paper duplicate pairs** (companion papers reporting the same samples; plus literature values quoted from "previous work by our group"), 3 of which **violate the README's own literature-comparison exclusion policy**.
- **11 of 63 `paper_title` values are not the title of their own DOI** (verified against Crossref); the DOI, k value and source location are correct — it is a metadata corruption that propagates into `paper_inventory.csv` and `extraction_log.csv`.
- **The QC report's claim "unit normalization: `normalize_k()` applied" is false** — the function is never called by any script. (Latent, not manifested: every row already carries a W/mK-family unit.)
- **1 of 188 k values (1.052, row `b639a9c9-159`) does not appear anywhere in its fulltext** — most plausibly a derived (1.278/1.214) or figure-digitized number presented in `source_location` as a direct Results value.
- **3 rows mislabel the measured sample** (Cu-hybrid labeled "BN"; a 0.0 wt% baseline labeled "cBN"; a trimodal Al2O₃+BN row labeled "AlN" — the string "AlN" has 0 hits in that paper).
- **3 screened papers were silently dropped** (fulltext on disk, in screening artifacts, in neither the dataset nor `unusable_sources.csv`).

**Verdict: CONDITIONAL PASS on k-value integrity, FAIL on metadata integrity and pipeline reliability claims.** No evidence of fabricated k values was found: all 188 values were string-located in their own paper's fulltext except the single 1.052 case; ~120 rows were additionally confirmed by context reading. Phase 2 (dedup + unit/title fixes) is mandatory before downstream analysis.

---

## 2. Claimed vs verified results

| Claim (README / QC report) | Claimed | Verified | Status |
|---|---|---|---|
| Total rows | 188 | 188 | ✅ match |
| Columns | 31 | 31 | ⚠️ match, but 2 columns are 100% empty (`filler_aspect_ratio`, `size_distribution`) |
| Unique papers / DOIs | 63 | 63 (identical sets in dataset and extraction_log) | ✅ match |
| Confidence split | 179 High / 9 Medium | 179 / 9 | ✅ match |
| k_composite range | 0.17 – 19.0 | 0.17 – 19.0 | ✅ match |
| Median k | 1.052 | 1.052 | ✅ match |
| Year range | 1997–2026 | 1997–2026 | ✅ match |
| Value source split | text 131 / table 57 | 131 / 57 | ✅ match |
| Extraction-log entries | 70 | 70 (63 papers + 7 retries) | ✅ match |
| Unusable sources | 48 | 48, zero overlap with dataset | ✅ match |
| QC "by filler" table | sums implicitly 188 | sums to 187 (omits the `filler_material='none'` neat-epoxy row) | ❌ minor mismatch |
| QC "unit normalization: `normalize_k()` applied" | applied | **never called anywhere** | ❌ false claim |
| README "validation rejects missing/non-numeric k, loading, source_location" | rejects | **rows appended anyway** (logged as "rejected") | ❌ false claim |
| README "literature-comparison values excluded" | excluded | 3 rows violate (141, 142, 151) | ❌ policy breach |
| README "hybrid fillers … `filler_material` contains 'hybrid'" | convention | 8 rows contain "hybrid"; rows 036, 151–153, 188, 095 hybrids/co-fillers do not | ⚠️ convention breach |
| QC exclusion examples (5 sampled) | present with reasons | all 5 exist in `unusable_sources.csv` with matching reasons | ✅ match |
| `work/rows_raw.jsonl` ≡ deliverable CSV | — | content identical (188 lines) | ✅ match |

---

## 3. Artifact existence and consistency checks

All seven claimed deliverables exist at the project root. SHA-256 (first 16 hex chars, recorded at audit end; files never opened for writing by the audit):

| File | sha256 (16) | Bytes |
|---|---|---|
| `thermal_conductivity_dataset.csv` | `78999ab6f289b68d` | 120,546 |
| `paper_inventory.csv` | `6d6ceca2efe18ec9` | 14,949 |
| `extraction_log.csv` | `bd459be54b86bd3e` | 27,225 |
| `uncertain_measurements.csv` | `cc8ab3b308051a03` | 6,980 |
| `unusable_sources.csv` | `c0c1ec7c18fd4e97` | 3,153 |
| `quality_control_report.md` | `6cb2e76643e7f981` | 4,281 |
| `README.md` | `05c04bc3f6e24214` | 4,760 |

Cross-artifact consistency:

- Dataset DOI set == extraction_log DOI set (63 vs 63, **zero difference** — no orphan rows, no log-only papers).
- `uncertain_measurements.csv` contains exactly the 9 Medium-confidence rows of the dataset.
- `unusable_sources.csv` (48) has **zero DOI overlap** with the dataset.
- `paper_inventory.csv` row counts sum to 188 and its per-paper k min/max agree with the dataset.
- Defect: the **same 11 wrong `paper_title` values** appear identically in `thermal_conductivity_dataset.csv`, `paper_inventory.csv`, and `extraction_log.csv` (single-source metadata corruption, not drift).
- Defect: exclusion decisions for the 48 unusable sources are **hardcoded in `work/build_deliverables.py`, not present in `extraction_log.jsonl`** — the log records only accepted papers/retries, so exclusion is not auditable from the log alone.
- `work/search_log.json` was written **after** the deliverables (retrospective, not contemporaneous); 7 entries (Crossref / Semantic Scholar / Europe PMC / Unpaywall / SearXNG).
- 3 files named `*.pdf` in `work/fulltext/` are **Radware Bot Manager captcha HTML** (1,437 bytes each) — correctly listed as unusable (`10.1088/1361-6528/ac0470`, `10.1088/1742-6596/1003_1_012082`, `10.1088/1757-899x/274_1_012043`).

---

## 4. Row-level verification results

**Method.** Two independent layers:

1. **Automated (188/188 rows):** search each row's `k_composite` (plus float-format variants) in its own DOI's fulltext file; require the filler-loading value to co-occur within ±500 chars; scan numeric columns for non-numeric values; pairwise duplicate detection on (doi, filler, loading, k).
2. **Manual context reading (~120 rows):** every base-warning row (22), every duplicate candidate (10 + 10 cross-paper), all 20 `polym13060955` loading rows (source Table 2 read directly), all 11 wrong-title paper headers, all 9 Medium rows, the full k ≥ 3 stratum, both mismatched-DOI abstracts, and a stratified sample of High rows. Titles for all 63 DOIs checked against fulltext headers; 11 mismatches re-fetched from Crossref.

**Final row statuses (all 188 rows classified in `work/audit_phase1_rows.json`):**

| Status | Rows | Meaning |
|---|---|---|
| `verified` | 110 | k located in own fulltext, context confirmed, no defects |
| `verified_with_warning` | 37 | value verified, but row carries a metadata/labeling defect (see §9) |
| `duplicate_measurement` | 19 | 9 intra-paper duplicates + 10 cross-paper duplicates (both sides flagged; drop recommendation in each finding) |
| `incorrect_value` | 17 | `filler_loading_wt_pct` stores parts, not wt% (paper states 58.0 wt%); k itself verified |
| `incorrect_sample_mapping` | 3 | rows 036, 147, 180 (filler label ≠ measured sample) |
| `out_of_scope` | 1 | row 151 (literature "previous work" value) |
| `not_verifiable` | 1 | row 159 (k = 1.052 absent from fulltext) |

**Key row-level confirmations (values independently re-read against source text/tables):** rows 107–114 (PI/BNNS in-plane 1.83/2.22/2.76/2.95 and out-of-plane 0.26/0.33/0.36/0.44 — exact sentence match); 174/175 (1.66 @298 K, 0.84 @77 K); 180 (1.64 trimodal); 184 (0.653 BN70/PU, with noted source-text inconsistency); 159–161 (1.182, 1.278 verbatim; 1.052 absent → `not_verifiable`); 182/183/185 (0.6 / 0.2 3D BN/PA66); 178/179 (0.58/1.44); 188 (1.10); 156/158 (0.58/1.03); 048 (0.372); 083 (0.65); 089 (1.04); 095 (0.9372); 126 (0.215); 151–153 (0.54 flagged as literature, 0.648/0.745 verified); 099/100/101/105/106/128/154/155/172/181/187 and all Medium rows (earlier passes).

**Duplicate pairs confirmed (later id = duplicate → drop):** `046/061`, `047/062`, `073/077`, `094/098`, `116/119`, `117/120`, `118/121`, `130/150`, `182/185`.
**Cross-paper pairs (both flagged; recommended drops):** `a9d63e6e-014/015/016` ↔ `d831a829-135/136/138` (same ETLBN30-70 samples, S1/S2/S4, companion papers — keep the 5-row pressure series `135–139`, drop `014/015/016`); `a8b6fee9-141/142` ↔ `e5a9c8bd-122/123` (same values 0.352/0.364 cited as "previous work by our group" — keep the primary `122/123`, drop `141/142`).

**Fabrication screen:** zero rows whose k string is absent from their own fulltext, except `b639a9c9-159` (1.052). All 11 wrong-title rows' values were verified present in the *correct* paper identified by the DOI — so the title corruption did not pull values from the wrong paper.

---

## 5. Unit normalization verification

- `normalize_k()` (defined at `work/io_append.py:24`) is **never invoked** by any extract script, by `append_rows`, or by `build_deliverables` (grep-verified). The QC report line "*unit normalization: `normalize_k()` applied*" is therefore **false as a process claim**.
- Independent unit test suite `work/audit_normalize_k_test.py` (26 designed cases): **24 PASS, 2 FAIL**:
  - `normalize_k(1.0, 'kW/mK') → 1.0` — expected `1000.0`. The kW prefix falls through to the generic fallback and is **silently not scaled**.
  - `normalize_k(1.5, 'μW/(m·K)') → 1.5` — expected `None`; the fallback accepts *any* string containing a w…k…m pattern and returns the value unscaled (micro-prefix ignored).
  - The explicit W/mK-family table entries (W/mK, W/(m·K), W m⁻¹ K⁻¹, W·m⁻¹·K⁻¹, Wm⁻¹K⁻¹, mW, W/cmK, W/mmK, lowercase-k variants, bullet operators) are all correct; unsupported units (`W/m°C`, `cal/(cm·s·K)`, empty) correctly return `None`.
- **Manifested impact: none.** All 188 rows have `k_original_unit` in the W/mK family and `k_original_value == k_composite_W_mK` for every row — i.e., normalization was never needed for current data, which is why the false claim went unnoticed. The defect is **latent**: any future kW/μW/other unit would be silently mishandled or the claim would remain wrong.
- Independent cross-check: `k_composite` range 0.17–19.0 is unit-consistent (the 19.0 and 7.5 rows are porous-AlN-skeleton vol% composites verified in source); no W/mW magnitude anomalies detected.

---

## 6. Pipeline reliability findings

1. **Validation does not reject (root cause of the duplicates).** `io_append`'s try/except for non-numeric `filler_loading_original_value` / `measurement_temperature_C` / `filler_mean_size_um` appends the row and records a "rejected" problem instead of skipping it (`continue` missing). The extraction log for P009 (`acsanm.4c01646`) states `rows_rejected_at_append: 2f8abcf1-046 … -047` — yet both rows exist in the final CSV. Retry scripts (`extract_005/008/010/013/018b/018c`) re-ran and appended again → **9 exact duplicate pairs**, 9 wasted rows.
2. **Retry idempotency absent.** No uniqueness key (`doi + sample + condition`) is checked before append.
3. **`fix_dois.py` rewrites `rows_raw.jsonl` in place** (non-atomic, no temp-file rename) — a crash mid-write would truncate the raw store. (File is currently intact, 188 lines.)
4. **No `try/except` swallowing in extract scripts** (good — the only failure-path bug is #1).
5. **Exclusions hardcoded in `build_deliverables.py`** rather than logged; `search_log.json` written retrospectively (see §3).
6. **`normalize_k` dead code** wired to nothing (see §5).
7. **README's stated validation guarantees overstate reality** (rejects → appends-while-logging).
8. **Screening-to-output leakage:** three papers were screened and fetched but appear in *neither* output (see §7).

Overall: the pipeline produces correct outputs **only when inputs are already clean**; its self-reported guardrails (rejection, normalization) do not actually execute.

---

## 7. Literature and full-text inventory coverage

- **63 accepted DOIs** — each has a fulltext file on disk, each appears in `extraction_log.csv` (1:1), and `paper_inventory.csv` covers exactly those 63.
- **Title/DOI match:** 52/63 dataset titles match their fulltext header; **11/63 do not** (Crossref confirms fulltext correct, dataset wrong):
  `10.1038/s41598-018-19945-3`, `10.3390/polym11121990`, `10.3390/polym11081335`, `10.3390/polym13030456`, `10.3390/nano15120936`, `10.3390/polym18050648`, `10.1039/c8ra10211b`, `10.3390/ijms24098221`, `10.3390/polym16081169`, `10.3390/polym17111507`, `10.3390/nano8120997`.
- **Unusable list (48):** reasons are defensible — 37 publisher blocks (403/captcha), 3 IOP captcha-PDFs (verified: HTML captcha on disk), 1 review, 1 modeling-only, 4 out-of-scope (carbon/PCM/Si₃N₄), 3 figure-only, 3 relative-%-only (some overlap in examples). 43/48 appear in `candidates.json`; 5 were sourced elsewhere (no provenance entry).
- **Preprint/published double-count:** handled correctly — `extraction_log` entry for `10.1021/acsanm.4c01646` explicitly records `duplicate_checks: preprint 10.26434/chemrxiv-2024-n9mn8 same study - not counted separately`; inventory contains the published DOI only. ✅
- **Silently dropped (neither dataset nor unusable list):**
  - `10.3390/polym11101548` — in `wave2_screen.json` (`n_k=2`, both hits are literature-comparison: epoxy 0.2 background, BN 320 filler property → legitimate exclusion) but **never recorded as excluded**;
  - `10.3390/polym15051214` — in `wave2_screen.json` (`n_k=0`) → exclusion unrecorded;
  - `10.3390/nano13152243` — in `candidates.json` + `screen_report.json`, dropped with no record.
  All three have fulltext on disk. Coverage gap for Phase 2: confirm polym11101548 truly has no own-data k values (recovery candidate).
- **Discovery provenance:** `candidates.json` (252 candidates), `epmc_wave2.json`, `wave2_screen.json` (33), `screen_report.json` all present in `work/`.

---

## 8. Plausibility screening

| Check | Result |
|---|---|
| k positive, in [0.17, 19.0], all numeric | ✅ 188/188 |
| k_composite < k_matrix (impossible rows) | ✅ 0 found (84 rows have empty `k_matrix`, allowed) |
| wt%/vol% loadings within 0–100 | ✅ all numeric fillings in range; non-numeric text lives in `filler_loading_original_value` (9 rows, §9 D9) |
| k_direction vocabulary | ⚠️ 11 distinct raw strings for ~5 concepts: `unknown` 130, `through-plane` 22 + 7 variant spellings (`through-plane (vertical alignment)`, `vertical`, …), `in-plane` 9 + malformed `sheet plane (in-plane` (unbalanced paren), `out-of-plane` 4 — not normalized |
| measurement_temperature_C filled | 12/188 (README says ambient-unless-set — consistent, but limits temperature-aware analysis) |
| Identical (doi, k, wt, vol) triples | exactly 9 → matches the 9 duplicate pairs |
| Extreme values | 19.0 / 7.5 W/mK: porous AlN skeleton vol% composites — verified in source text; 0.17: neat/silicone baselines — plausible |
| Median 1.052 | reproduces exactly; ironically equals the one unverifiable value |
| Scope outliers retained by design | neat-epoxy baseline row `caf49a8d-129` (flagged), optional matrices (silicone/PI/PDMS/PEG/PS/PU) tagged per README |

---

## 9. Issues found (prioritized)

**P0 — must fix before any analysis**

- **D1 · Validation appends rows it reports as rejected → 9 duplicate pairs** (rows `061,062,077,098,119,120,121,150,185`). Evidence: `io_append.py` control flow; log/CSV contradiction for `2f8abcf1-046/047`. Impact: dataset is 188 rows but only **179 unique measurements**; any per-row statistic is biased by up to 5%.
- **D2 · Loading mislabeled for 20 rows** (`a9d63e6e-010…029`): `filler_loading_wt_pct` = formulation parts (60/70/65) while paper states **58.0 wt%** for the -70 grade ("58.0 wt.% BN" appears verbatim); vol% column correct. Impact: any wt%-based model/training on these rows is wrong by ~20% relative.
- **D3 · 5 cross-paper duplicate pairs** (10 rows): `014/015/016` ↔ `135/136/138` (same samples, companion papers); `141/142` ↔ `122/123` (cited previous-work values — also policy violations). Impact: double-counts three measurement conditions twice.
- **D4 · False QC claim** "`normalize_k()` applied" + **2 failing unit tests** (kW/mK unscaled; μW silently accepted). Latent today, wrong claim regardless.

**P1 — must fix before publication**

- **D5 · 11 wrong `paper_title` values** (not the DOI's Crossref title) in all three metadata files. Values/DOIs verified correct.
- **D6 · 3 sample mislabels**: `036` Cu-hybrid labeled "BN"; `147` 0.0 wt% baseline labeled "cBN"; `180` Al₂O₃+BN row labeled "AlN" (string absent from paper). Plus hybrid-label convention breaches on `151/152/153/188/095`.
- **D7 · `b639a9c9-159` k=1.052 not in fulltext** — undisclosed derivation or figure digitization (`source_location` presents it as a direct Results quote; plausible value = 1.278/1.214).
- **D8 · Policy violations**: literature-comparison rows `141/142/151` despite README exclusion rule.
- **D9 · Non-numeric values in numeric fields** (9 rows: **2 true numeric-column violations** — `filler_mean_size_um` = `55 (AlN) / 35 (BN)` @130, `measurement_temperature_C` = `RT` @094 — plus **7 unparsable composite strings** in the text column `filler_loading_original_value` @046/047/073/116/117/118/182) — the log claims these inputs were rejected at append.
- **D10 · 3 silently dropped screened papers** missing from both outputs (polym11101548, polym15051214, nano13152243).

**P2 — cleanup**

- **D11 · Row-level metadata**: curing-agent ratio `100:38` vs source `100:35` (+ "LY654" typo) on `046/047`; unsupported `k_direction='through-plane'` + 6.32 vs 6.33 vol% on `105`; neat-epoxy row `129`; paper-internal BN60/BN70 inconsistency on `184`; 2 empty schema columns; `k_direction` vocabulary not normalized (§8).
- **D12 · Process**: exclusions hardcoded not logged; retrospective `search_log.json`; 5 unusable DOIs absent from candidates; `fix_dois.py` non-atomic rewrite; QC "by filler" table sums to 187.

---

## 10. Recommended remediation plan (Phase 2+)

**Phase 2a — data fixes (mechanical, no re-reading papers needed)**

1. Dedup: drop `061,062,077,098,119,120,121,150,185` (intra-paper) → 179 rows.
2. Cross-paper dedup: drop `a9d63e6e-014/015/016` and `a8b6fee9-141/142`; decide `4a11b03c-151` (drop or re-source to original DOI) → 174 rows.
3. Fix `filler_loading_wt_pct` for `a9d63e6e-*` from source Table 2/text (58.0 wt% for -70 grades; recompute -60/-65 grades from the paper's stated formulations); keep parts in `filler_loading_original_value` with proper unit.
4. Overwrite the 11 wrong titles from Crossref into dataset + inventory + log (single script, 11 API calls).
5. Fix `filler_material` for rows `036` (hybrid Cu/BN/PI), `147` (neat), `180` (Al2O3+BN trimodal); apply README hybrid convention to `151/152/153/188/095`.
6. Re-source or drop `159` (disclose derivation/digitization in `value_source`/`source_location`).
7. Fix the 2 true numeric-column violations (`55 (AlN) / 35 (BN)` → per-filler sizes in notes; `RT` → ambient/blank) and split the 7 unparsable composite loading strings in `filler_loading_original_value` into value+detail.
8. Record the 3 dropped papers in `unusable_sources.csv` with reasons; re-verify polym11101548 for own-data k (recovery candidate).

**Phase 2b — pipeline hardening**

9. `io_append`: make validation failures *skip* the append; add idempotency key `(doi, sample, loading, k)`; atomic writes (temp + `os.replace`) for `rows_raw.jsonl` and deliverables.
10. Wire `normalize_k` into `append_rows` (or delete the claim); fix kW/μW fallback (return `None` for unknown prefixes; multiply kW by 1000).
11. Log exclusion decisions at screening time with reason codes; write `search_log.json` contemporaneously.
12. Normalize `k_direction` to a controlled vocabulary (`in-plane|through-plane|unknown`), move variants to notes; fill or drop empty columns; correct QC "by filler" table (188, add `none` row).
13. Re-run QC report generation so its claims describe what the pipeline actually did.

**Phase 3 (optional, needs access):** pursue the 37 publisher-blocked candidates; digitize the 3 figure-only papers (already classified unusable).

---

## 11. Commands run (with exit codes)

| # | Command (abbrev.) | Exit | Outcome |
|---|---|---|---|
| 1 | `git rev-parse --is-inside-work-tree` | 128 | not a git repository |
| 2 | `python -c` structural/statistical recomputation (rows, cols, counters, median, ranges, sha256) | 0 | all claimed stats reproduce |
| 3 | `python -c` dataset↔log↔inventory↔unusable DOI-set cross-checks | 0 | 1:1 log/dataset; 0 unusable overlap; 3 orphan fulltexts identified |
| 4 | `grep -rn "normalize_k"` (project) | 0 | defined once, never called |
| 5 | `python work\audit_normalize_k_test.py` | 0 | 26 cases: 24 PASS / **2 FAIL** (kW, μW fallback) |
| 6 | `python work\audit_evidence_check.py` | 0 | 188 rows classified: 166 verified / 13 warning / 9 dup (base layer) |
| 7 | `python work\audit_finalize_rows.py` | 0 | manual layer applied → 110/37/19/17/3/1/1 |
| 8 | `python -c` loading co-occurrence window check (188 rows) | 0 | 34 flags, all manually reviewed → 1 real (`159`) |
| 9 | `python -c` paper_title vs fulltext-header check (63) | 0 | 11 mismatches found |
| 10 | `webfetch api.crossref.org/works/{doi}` ×11 | 0 | dataset titles confirmed wrong; fulltexts confirmed correct |
| 11 | `python work\audit_tmp_lists2.py` (provenance/chemrxiv checks) | 0 | preprint dedup correct; wrong titles propagate to inventory/log |
| 12 | `python -c` plausibility (matrix vs matrix, loadings, direction vocabulary, dup triples) | 0 | 0 impossible rows; 9 dup triples; direction not normalized |
| 13 | `python -c` inline (first attempt) | **1** | PowerShell nested-quote SyntaxError; rerun as script file (exit 0). Tooling incident only. |
| 14 | `python -c` context reads of fulltext for ~60 targeted rows/DOIs (multiple invocations) | 0 | values verified / defects extracted |

*(All audit runs used `$env:PYTHONIOENCODING='utf-8'`. No command modified any pre-existing file.)*

---

## 12. Confidence statement

**High confidence (directly verified this session):**
- All structural/statistical claims (§2) — recomputed from files.
- The 9 intra-paper duplicate pairs and their root cause (code read + log/CSV contradiction).
- The 20-row loading mislabel (paper text read: parts vs "58.0 wt.%").
- The 5 cross-paper duplicate pairs (both papers' tables/text read).
- The 11 wrong titles (Crossref API + fulltext headers).
- `normalize_k` never called (grep) and its 2 test failures (executed).
- The 3 sample mislabels (fulltext context reads; "AlN" 0 hits).
- `159` k=1.052 absent (exhaustive string search).
- 3 silently dropped papers (screening artifacts read).
- Non-numeric-in-numeric 9 rows, empty columns, direction vocabulary, QC 187-sum.

**Verified but narrower basis (state as such downstream):**
- The ~100 rows classified `verified` solely by the automated k+loading co-occurrence check — value strings and loadings co-occur in the right paper, but tables were not independently re-read line-by-line.

**Suspected / unresolved (needs Phase 2/3):**
- Whether `1.052` is derived (1.278/1.214) or digitized from Figure 5 — both plausible, neither documented.
- Whether `polym11101548` truly contains no own-data k values (screening showed only literature-comparison hits).
- Which of the two companion ETLBN30-70 papers should "own" the three shared rows (recommendation: keep `d831a829-135…139` pressure series) — a domain-owner decision.
- Completeness vs the 37 publisher-blocked papers (out of Phase-1 scope by design).
- No publisher-site verification was performed; all paper facts come from local fulltext/EPMC copies plus Crossref metadata.

**Not claimed:** no claim is made that every remaining `verified` value was manually re-derived from its source table — coverage numbers above are stated explicitly (188 automated / ~120 manual).

---

## 13. Files created (new; no existing file modified)

| File | Purpose |
|---|---|
| `audit_phase1_report.md` | this report |
| `work/audit_phase1_results.json` | repo-level results: claim table, defect register, tests + exit codes, verdict |
| `work/audit_phase1_rows.json` | per-row verification status + findings for all 188 rows |
| `work/audit_evidence_check.py` | automated k-in-fulltext / numeric-column / duplicate checker (base layer) |
| `work/audit_normalize_k_test.py` | 26-case independent unit test for `normalize_k()` |
| `work/audit_finalize_rows.py` | applies manual-verification layer to the row results |
| `work/audit_tmp_lists.py`, `work/audit_tmp_lists2.py` | throwaway helpers (provenance/title checks) |
| `work/audit_phase2_inputs.py` | Phase-2 prep builder (read-only): titles, loading fixes, drop lists, non-numeric split; baseline-hash guarded, exit-code checked |
| `work/audit_phase2_inputs.json` | machine-readable Phase-2 inputs: 11 Crossref title corrections (11/11 verified present in own fulltext), 20 loading fixes (Table-1 weight basis), 15 drop candidates, 9 non-numeric cells (2+7) |

---

## 14. Next actions

1. **Approve Phase 2a data fixes** (dedup 14 rows → 174, loading correction for 20 rows, 11 title overwrites, 3 sample-label fixes, row-159 decision) — all scripted, re-runnable, reversible against the recorded SHA-256 hashes.
2. **Approve Phase 2b pipeline hardening** (reject-means-skip, idempotency, atomic writes, `normalize_k` wiring + kW/μW fix, exclusion logging, direction vocabulary).
3. Domain-owner call: keep-side choice for the ETLBN30-70 cross-paper triplicate; fate of `4a11b03c-151` (drop vs re-source).
4. Optional recovery pass on `polym11101548` / `polym15051214` / `nano13152243` and the 37 blocked sources (Phase 3).
5. Re-generate `quality_control_report.md` from the fixed pipeline so its claims match observed behavior, then re-run this audit as Phase 2 verification.
