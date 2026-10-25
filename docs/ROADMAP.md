# ARGUS roadmap

Status as of 2026-10-25. Architecture: [ARCHITECTURE.md](ARCHITECTURE.md). Research basis:
[research report](reports/BN%20epoxy%20thermal%20conductivity%20research.md).

| Phase | Goal | Status |
|---|---|---|
| 0 | Legacy dataset v1.0 (260 rows / 95 papers, ad-hoc scripts) | ✅ done (before this plan) |
| 1 | Foundation: records, validation, build, verify, tests | ✅ done |
| 2 | Normalisation and enrichment | ✅ core done, follow-ups open |
| 3 | Physics models and fits | 🟡 started |
| 4 | Measurement-bias analysis (course centrepiece) | ✅ core done, follow-ups open |
| 5 | Machine learning with honest validation | ✅ core done, follow-ups open |
| 6 | Acquisition at scale | ⏳ |
| 7 | Explorer, release and course report | ✅ done (Zenodo DOI needs your account) |
| 8 | External validation against other groups' data | ✅ done |

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

## Phase 5: Machine learning ✅

The research report set the bar: published R² of 0.95–0.99 come from random splits and collapse when whole
papers are held out.

Delivered:
- `argus ml benchmark` writes [`reports/ml_benchmark.md`](../reports/ml_benchmark.md), the JSON results,
  per-row leave-one-paper-out predictions with 90% intervals (`ml_lopo_predictions.csv`), and a parity
  plot.
- **Setup:** 27 features in 10 groups (loading, physics, filler, morphology, treatment, direction, method,
  matrix, quality, year). The target is log₁₀(k/k_m). There are 218 single-filler rows from 80 papers.
- **Models:** baselines (median; calibrated Nan 1997; 5-nearest-neighbours on loading + filler) against
  ridge (alpha chosen by grouped inner CV), physics + Gaussian-process residual, gradient boosting
  constrained to be non-decreasing in loading, and a random forest.
- **Validation:**
  - Leave-one-paper-out (headline) and repeated 5-fold by paper.
  - Row-level 5-fold, shown only to expose leakage.
  - A time split (train ≤ 2021) and leave-one-filler-family-out.
  - Paper-grouped conformal intervals.

Findings (acceptance **passed**):
- **Accuracy on an unseen paper:** gradient boosting predicts k within a typical **factor of 1.66** (MAE
  0.221 log₁₀, R² 0.59, 75% within ×2). The baselines reach ×1.91 (nearest neighbours) and ×2.14 (physics).
  This sits inside the research report's realistic range (×1.4–2).
- **Monotonicity trade-off:** constraining every loading-derived feature (φ, φ², physics, Maxwell ceiling)
  costs about 0.02 in MAE against constraining φ and physics only (0.202). It is kept, because the looser
  model can predict k falling as loading rises.
- **Leakage:** row-level splits overstate accuracy by up to 0.09 log₁₀ (Gaussian process: 0.152 vs 0.242),
  enough to turn an honest ×1.75 into an apparent ×1.42.
- **Intervals:** paper-grouped 90% intervals are calibrated (90% coverage) but wide (×/÷3.4); 68% intervals
  are about ×/÷1.9.
- **Which information matters:**
  - Loading + physics carry most of the information (removing both: +0.13).
  - Measurement direction is the only other group that clearly helps (+0.03), echoing Phase 4.
  - Morphology, treatment, matrix and year are not distinguishable from noise with 80 papers.
- **Over time:** the newer-paper time split is harder (×1.86 for ridge, the best on it). Papers from 2022
  on have more BNNS and aligned fillers and a lower median enhancement.

Next:
1. Per-component loading for the 34 hybrid rows, so they can enter the model.
2. Add `tps_mode` and `lfa_holder` once recorded (Phase 4 follow-up). Direction is the most useful metadata
   after loading.
3. Re-run the benchmark after each data release, and track the LOPO MAE in `data/CHANGELOG.md`.

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

## Phase 7: Explorer, release and course report ✅

Done:
- **Course report** → [docs/course_report/COURSE_REPORT.md](course_report/COURSE_REPORT.md).
  - `argus report course` renders it from the analysis outputs, with 7 figures.
  - Structure: characterisation techniques → data and methods → method bias → physics → prediction →
    reporting checklist.
  - Every dataset number is a template variable. Rendering refuses analysis outputs whose dataset fingerprint
    differs from the current records, or that came from a `--quick` run.
- **CI:** GitHub Actions runs validate, `pytest` and `argus verify` on every pull request and every push to `main`.
- **Interactive explorer** → `docs/explorer/index.html`, generated by `argus report explorer`. It is one
  self-contained page with no chart library.
  - **Filters:** filler, matrix, technique, direction, source and free-text search.
  - **Colour-by views:** four (filler, technique, direction, source), each folded to three groups so the
    palette stays colour-blind safe.
  - **Chart:** k or k/k_m against vol% on a log axis, with Maxwell-ceiling and Nan 1997 reference curves.
  - **Provenance:** a hover tooltip, a pinned detail card with the verbatim source quote and DOI link, and
    a sortable table view with a CSV copy.
  - **Publishing:** `explorer.artifact.html` is the same page as a fragment for a shareable link. The
    repository is private, so GitHub Pages would need a paid plan.

- **Versioned release:** tag `data-v1.1` on `main`.
  - Authors are Aniket Kumar and Rao Kumar Srinidhi Reddy, and appear in the report and the explorer.
  - `CITATION.cff` is generated from `data/dataset.yaml` and checked by `argus verify`.
  - Licences: data under CC BY 4.0 (`LICENSE-DATA.md`), code under MIT (`LICENSE`).

Next:
1. **Zenodo DOI.** Connect the repository in Zenodo's GitHub integration (needs your Zenodo account), then
   publish a GitHub Release from `data-v1.1` to mint a DOI. Add the DOI to `data/dataset.yaml`.
2. **Before going public:** review the third-party papers in `work/fulltext/`, which keep their own licences
   (two are non-commercial, CC BY-NC), and remove the three saved captcha pages, which embed the
   fetching machine's IP address. See the checklist in `LICENSE-DATA.md`.
3. **Report finishing:** a PDF/Word export if the course requires one.

---

## Phase 8: External validation ✅

Goal: test the physics code, the models and the extracted values against data that other groups curated.
Design: [ARCHITECTURE.md §8c](ARCHITECTURE.md#8c-external-validation). Results:
[reports/external_validation.md](../reports/external_validation.md) and Section 4.5 of the course report.

Search: a parallel sweep of data repositories, code hubs, paper supplements and materials databases, with
independent verification of each candidate's licence, access and contents. Kept (`data/external/README.md`):
- **EVF** (Anastasiou 2026, CC BY 4.0): 137 polymer + ceramic points from 14 papers, none in ARGUS.
- **He, Wu & Fu 2025** (*Nat. Commun.*): the MIT source data for physics checks, and Supplementary Data 1
  (CC BY-NC-ND, fetched on demand) with 131 test points from 22 papers.
- **Sarikhani et al. 2022** (CC BY 4.0): two transcribed BN datasets, one test set and one cross-check.
- **Mumtaz et al. 2024** (CC BY-NC-ND): two rows used for a value cross-check.

Rejected: simulated datasets (lattice Boltzmann, FEM), datasets with no released data (several ML papers),
registration-only or no-redistribution databases (PoLyInfo, NIMS CompoTherm, MaterialsMine), and
low-provenance compilations.

Done:
- **Physics code verified.**
  - Maxwell–Garnett, symmetric Bruggeman, Hasselman–Johnson and the Voigt–Reuss mean reproduce both
    workbooks' published predictions to ≤10⁻⁹ (1,032 point-by-point comparisons).
  - Asymmetric Bruggeman agrees at 171 of 242 points. At the rest, the published values fail the model's
    equation while ours solve it to 10⁻¹³. Most gaps are below 1% (solver tolerance); 20 are larger,
    including a few rows that appear shifted within one series.
- **Transfer.** Trained only on ARGUS, predicting 274 measurements from 34 unseen papers:
  - the best model, the ensemble, reaches ×1.39 against ×1.48 for calibrated physics. With 34 test
    papers the gap is not yet distinguishable from zero (95% CI of the MAE difference −0.057 to +0.008);
  - on EVF alone, physics + Gaussian process is clearly better than physics;
  - the ensemble's 90% intervals cover 98% of rows;
  - the random forest, competitive inside ARGUS (second among single models), is clearly worse than
    physics on unseen literature, and its intervals under-cover (89%).
- **Pooled training.** Adding the external papers clearly improves gradient boosting on ARGUS's own
  papers (MAE 0.236 → 0.219); the other models change within noise. On the external papers themselves
  pooling clearly helps most models, the random forest above all (0.30 → 0.11).
- **Value cross-check.**
  - 3 shared papers, 4 paired values: 3 exact matches. The one difference traces to a review that pairs
    the 20 vol% value with 15 vol%.
  - A compilation lists loadings above the source paper's stated maximum.
  - No ARGUS value changed. See `data/external/crosscheck_review.yaml`.
- **Improvements adopted:**
  - **Ensemble model:** best leave-one-paper-out MAE inside ARGUS (×1.67) and best on external data
    (×1.39), with ×/÷3.3 intervals.
    - It was chosen on ARGUS only, comparing combinations on the same folds that report it, so its edge
      inside ARGUS (0.010 in log₁₀ over the random forest) is not evidence by itself.
    - On external data it is the best model, but not clearly better than physics alone.
  - **Publication year dropped as a feature.**
    - Inside ARGUS its ablation effect was within noise (+0.007 ± 0.008).
    - With the external rows' real years, gradient-boosting error on external data rose from 0.147 to
      0.250, and the ensemble's from 0.132 to 0.179: year acted as a proxy for paper identity.
    - Without it, leave-one-paper-out MAE inside ARGUS rises slightly (ensemble 0.218 → 0.223, gradient
      boosting 0.221 → 0.236).
  - **Vocabulary:** THW, GHP, HFM and "TPS, …" abbreviations are now classified.
  - **Reference properties:** SiO₂, glass, Si₃N₄, SiC and ZnO.
  - **Explorer:** an optional layer showing other groups' data (CC BY only).
- **Independent code review** (5 reviewers, every finding re-checked by a skeptic): 23 confirmed
  findings fixed. They include:
  - Tian 2023 split into two "papers";
  - external rows lacking their publication year and figure provenance;
  - two blocks whose matrices are not epoxy thermosets, and one row with a pre-filled matrix (all excluded);
  - "GHP, DRL-III" misclassified;
  - report wording that overstated the results.
  The numbers above are after these fixes.
- **Tried and rejected:** a differential-effective-medium (asymmetric Bruggeman) feature.
  - Unconstrained, it lowered gradient-boosting error on ARGUS (LOPO 0.221 → 0.208).
  - The gain vanished once the feature was constrained to be monotone in loading, as every
    loading-derived feature is. It therefore relied on unphysical behaviour.

Next:
1. If the full text of P081 (Han et al. 2019) becomes accessible, add its in-plane Fig. 1(d) series. Two
   secondary sources agree on it.
2. Re-run `argus external validate` whenever a dataset version changes. It is fingerprinted like every
   other analysis.

---

## Known open data items

| Item | Where | Action |
|---|---|---|
| 28 abstract-only rows (Medium) | `uncertain_measurements.csv` | Upgrade when full text becomes OA |
| 28 figure-digitised rows (Medium) | P094, P095 | Keep; add per-point resolution to notes |
| Companion-paper ownership of the ETLBN30-70 series | P002 vs P094 | Domain-owner decision (audit §12) |
| `filler_aspect_ratio`, `size_distribution` almost empty | schema | Fill from full texts or drop in a schema v2 |
| QC report and FINAL_REPORT describe v1.0 | root | Regenerate from `argus stats` (Phase 2, item 5) |
