# ARGUS roadmap

Status as of 2026-10-22. Architecture: [ARCHITECTURE.md](ARCHITECTURE.md). Research basis:
[research report](reports/BN%20epoxy%20thermal%20conductivity%20research.md).

| Phase | Goal | Status |
|---|---|---|
| 0 | Legacy dataset v1.0 (260 rows / 95 papers, ad-hoc scripts) | ✅ done (before this plan) |
| 1 | Foundation: records, validation, build, verify, tests | ✅ done |
| 2 | Normalisation and enrichment | ✅ core done, follow-ups open |
| 3 | Physics models and fits | 🟡 started |
| 4 | Measurement-bias analysis (course centrepiece) | ✅ core done, follow-ups open |
| 5 | Machine learning with honest validation | ⏳ |
| 6 | Acquisition at scale | ⏳ |
| 7 | Explorer, release and course report | ⏳ |

---

## Phase 1: Foundation ✅

Delivered:
- The `argus` package (`src/argus`) with the `validate`, `build`, `verify`, `stats`, `physics`, `new-paper`
  and `migrate-legacy` commands.
- 95 per-paper record files as the source of truth, migrated from `work/rows_raw.jsonl`. The migration is
  proven lossless: all five deliverable CSVs rebuilt byte-identical.
- 21 validation rules. Errors block the build, and exceptions need a written waiver.
- Fixes for audit defects D1 (append-after-reject), D4 (unit normaliser) and the non-atomic writes, plus
  an identity key for duplicates.
- Release checks in `argus verify`, including "every change since v1.0 is declared" and tombstones.

Dataset **v1.1** (258 rows) closes these audit items. Details are in [data/CHANGELOG.md](../data/CHANGELOG.md).
- **D7:** removed a back-calculated value.
- **D10:** recorded the two papers that were silently dropped.
- **Hybrid labels:** corrected four.
- **Stale exclusions:** repaired two.
- **wt% basis:** fixed 11 rows in P094.
- **Model value:** removed one model-predicted value.

## Phase 2: Normalisation and enrichment ✅ (core)

Delivered:
- Vocabularies for 13 measurement-method classes, direction (including `mixed`), filler and matrix.
- wt% ↔ vol% conversion with labelled bases.
- An enriched table with 25 derived columns and bias flags, plus `datapackage.json`.
- An enrichment QA report, including a density self-check against rows that report both bases.

Open follow-ups:
1. **Verify reference values** marked `verified: false` in `reference/materials.yaml`: densities of cBN,
   Al₂O₃, MgO, silicone and polyimide; intrinsic k of BNNS, cBN, Al₂O₃ and MgO. Acceptance: every entry
   cites a primary or handbook source.
2. **Record Cp and density provenance** for LFA rows (DSC vs assumed; Archimedes vs rule of mixtures), as
   optional record fields. Acceptance: `lfa_cp_rho_unreported` drops from 68 by reading the method
   sections.
3. **Resolve the 83 `UNSPECIFIED` methods** where full text exists (56 rows are not abstract-only).
   Acceptance: under 40 remain, all of them abstract-only or genuinely unstated.
4. **Hybrid loading**: per-component vol% for the 26 hybrid rows that have no volume fraction, so they
   can enter physics fits.
5. **Regenerate the narrative docs** (README numbers, QC report sections) from `argus stats` so prose can't
   drift from data.
6. **Tidy the repo**: the root `rows_raw.jsonl` and `extraction_log.jsonl` are stale Phase-2 copies
   (173 rows). Move them into `work/` or delete them after confirming nothing reads them.

## Phase 3: Physics models 🟡

Delivered:
- The model library (12 models, conventions enforced and tested).
- One-parameter fits per loading series.
- First findings: 98% of rows exceed the Maxwell ceiling, and the median apparent R_K is
  6.8×10⁻⁷ m²K/W (see ARCHITECTURE §8).

Next:
1. **Orientation from metadata**: map `filler_alignment` × `direction_effective` to ⟨cos²θ⟩
   (vertical/aligned → 0 for through-plane k; in-plane film → 1 for through-plane, 0 for in-plane).
   Refit Nan with it.
2. **Percolation**: a combined Nan + Foygel fit for series above ~23 vol%; report φ_c and β per paper.
3. **Fair model comparison**: report AICc and leave-one-point-out error, not just RMSE (Agari has 2
   parameters).
4. **Geometry sensitivity**: the R_K fits assume p = 0.05 (h-BN) / 0.01 (BNNS) and 10 µm platelets.
   Publish the R_K spread over p ∈ [0.01, 0.2].
5. **Figures** for the course report: k/k_m vs φ with model bands; fitted R_K by functionalisation.

Acceptance: `reports/physics_summary.json` includes orientation-aware Nan fits for every series with known
alignment, and every fitted parameter carries its convention.

## Phase 4: Measurement-bias analysis ✅ (course centrepiece)

Question: how much does the characterisation technique change the reported k of BN/epoxy composites?

Delivered:
- `argus analyze bias` → [`reports/method_bias.md`](../reports/method_bias.md), `method_bias.json`, and
  `uncertainty_budget.csv` (per-row σ).
- A dependency-free REML mixed model (`src/argus/analysis/lmm.py`) with between/within degrees of freedom.
  It is checked against dense-matrix REML and synthetic recovery tests.

Findings:
- **Same-sample pairs.** 7 samples are reported both in-plane and through-plane, with k_in/k_through median
  6.7 (films 6.7–7.7; 3D networks 0.96–2.1). By the √(k_in·k_through) rule, an isotropic-mode Hot Disk or
  hot bridge would read up to **2.8×** the laser-flash through-plane value on those samples.
- **No sample was measured by two techniques.** The direct method effect cannot be measured from this
  literature.
- **Between papers** (190 rows / 65 papers, BN platelets), isotropic-mode sensors read **1.43×** laser flash
  (95% CI 0.86–2.36). That is the expected direction, but the interval includes 1. A naive regression that
  ignores papers would wrongly claim 1.10–1.75.
- **Paper-to-paper scatter** (factor 1.88 at 1 SD; ICC 0.78) dwarfs instrument precision (~5–10%).
- **Abstract-only rows appear biased upward**: abstracts quote a paper's best result.

Next:
1. **Same-sample multi-method data** is the decisive missing evidence. Search specifically for papers that
   report one sample by LFA *and* TPS (or TPS isotropic *and* anisotropic modes), or measure a few
   BN/epoxy samples in the course lab.
2. **Record the TPS mode** (isotropic / anisotropic / slab) and the LFA holder (standard / in-plane) as
   record fields when the method section states them.
3. **Feed the bias model into ML (Phase 5)**: method group and the abstract-only flag as covariates; weight by
   `rel_sigma_total`.

## Phase 5: Machine learning ⏳

The research report sets the bar: published R² of 0.95–0.99 come from random splits and collapse when
whole papers are held out.

1. **Features**: φ (with basis), filler family/base, shape, size, functionalisation class, alignment,
   `direction_effective`, `method_class`, k_m, and physics predictions (Nan R_K = 0, Lewis–Nielsen) as
   features or offsets.
2. **Target**: log₁₀ k or log₁₀(k/k_m).
3. **Models**: regularised linear model on physics features; Gaussian process with an EMT mean;
   monotone-constrained gradient boosting (xgboost is installed); random forest as baseline. Avoid deep
   nets and SVR.
4. **Validation**: GroupKFold and leave-one-paper-out by DOI, with all preprocessing inside the folds; also
   leave-filler-family-out and a time split. Report the random-split score only to show the leakage gap.
5. **Uncertainty**: group-aware conformal intervals; check calibration.

Acceptance: beat both the physics-only baseline and a nearest-neighbour baseline on leave-one-paper-out MAE
in log₁₀ k. A realistic target is 0.15–0.30, i.e. a factor of 1.4–2.

## Phase 6: Acquisition at scale ⏳

Target: 500+ rows from 200+ papers without lowering the provenance standard.

1. **Discovery**: OpenAlex with an API key (required since Feb 2026; $1/day free; search $1 per 1,000
   calls), Crossref with `mailto` (list queries 3 req/s), Europe PMC. Log every query contemporaneously.
2. **Screening**: title/abstract screening with ASReview LAB 2. Every decision goes to `exclusions.yaml`
   at screening time with a reason code.
3. **Full text**: Europe PMC JATS first, then OpenAlex TEI, then the OA PDF via Docling (Marker/MinerU as a
   cross-check). Gate every fetch on a recorded licence; cache under `sources/`.
4. **Extraction assist**:
   - A JATS table parser proposes candidate rows.
   - LLM extraction returns schema-validated JSON plus a verbatim quote. A check confirms the quote is in
     the source text, and ChatExtract-style follow-up questions run before acceptance.
   - A human approves the candidates into a record file.
   - The 258 current rows are the gold set; extractor precision and recall are scored in CI.
5. **Figures**: generalise `work/phase4_digitize_v2.py` (tick calibration, colour masks), storing
   resolution and occlusion notes. Priority candidates: polym11101548 and polym15051214 (Fig. 5),
   ma18215011 (Fig. 5a), polym10030277.
6. **Blocked sources**: about 200 publisher-blocked DOIs; pursue author manuscripts and repositories only.

## Phase 7: Explorer, release and course report ⏳

1. A static explorer (filter by filler, matrix, method, direction; k vs φ with model overlays), published
   as an artifact or GitHub Pages.
2. A versioned release: tag `data-v1.1`, `CITATION.cff`, a Zenodo DOI, and a data licence statement.
3. CI: GitHub Actions running `pytest` and `argus verify` on every pull request (workflow included).
4. The course report, structured as: characterisation techniques → dataset → measurement bias → physics →
   ML.

---

## Known open data items

| Item | Where | Action |
|---|---|---|
| 28 abstract-only rows (Medium) | `uncertain_measurements.csv` | Upgrade when full text becomes OA |
| 28 figure-digitised rows (Medium) | P094, P095 | Keep; add per-point resolution to notes |
| Companion-paper ownership of the ETLBN30-70 series | P002 vs P094 | Domain-owner decision (audit §12) |
| `filler_aspect_ratio`, `size_distribution` almost empty | schema | Fill from full texts or drop in a schema v2 |
| QC report and FINAL_REPORT describe v1.0 | root | Regenerate from `argus stats` (Phase 2, item 5) |
