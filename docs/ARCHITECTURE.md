# ARGUS architecture

ARGUS is a source-verified dataset of **measured effective thermal conductivity (k)** for polymer–ceramic
composites (mainly epoxy + h-BN / BN nanosheets / AlN), the materials used as thermal interface and
packaging materials for semiconductor devices. It is also the toolkit that curates, checks, enriches and
analyses that dataset.

This document describes the system as built (v0.2 toolkit, dataset v1.1) and the components the
[roadmap](ROADMAP.md) adds. Design choices draw on the research report
[`docs/reports/BN epoxy thermal conductivity research.md`](reports/BN%20epoxy%20thermal%20conductivity%20research.md),
cited below as *the research report*.

---

## 1. What problem the architecture solves

The v1.0 dataset (260 rows, 95 papers) was produced by about 150 one-off scripts in `work/`. Its values
were carefully checked, but the pipeline itself had defects that the Phase-1 audit documented:

| Legacy defect | Effect | Fixed by |
|---|---|---|
| Rows that failed validation were logged as "rejected" and appended anyway (D1) | 9 duplicate pairs | `validate.py`: errors block `argus build`; nothing is written |
| No identity key for a measurement | Retries re-appended rows | `duplicate_measurement` rule on the sample/condition/value key |
| Non-atomic rewrites of the master file | Risk of a truncated file | `io.atomic_write_*` (temp file + `os.replace`) |
| Unit normaliser never called; kW and μW not scaled; anything with w, m, k accepted (D4) | Latent wrong values | `units.py` with a strict parser; the `k_normalized_consistent` rule runs it on every row |
| Exclusions hard-coded in a build script (D10) | Unauditable drops | `data/exclusions.yaml`, checked against the dataset |
| Verification silently regenerated CSVs on mismatch | Hid drift | `argus verify` is read-only and fails on drift |

Measurement physics adds a second problem. For anisotropic BN platelet composites, **the measurement
technique shifts the reported k by more than the instrument's stated uncertainty**. Isotropic-mode Hot Disk
reports roughly √(k_in·k_through), laser flash on a disc reports through-plane k, and a single-thickness
D5470 rig includes contact resistance (research report, §1). An analysis-ready dataset therefore has to
record *what each method senses*, not just its name.

## 2. Principles

1. **Zero inference in the published data.** A value enters only if it is printed in the source (text or
   table) or pixel-digitised from a source figure by a reproducible script. Values that are back-calculated,
   model-predicted or quoted from other papers are excluded. Two such rows were removed in v1.1.
2. **One reviewable file per paper is the source of truth.** `data/records/P###_<doi>.yaml` holds the paper
   metadata, its extraction log and every measurement. A pull-request diff shows exactly what changed.
3. **Derived values are labelled, never mixed in.** Enrichment adds columns with a companion `*_basis`
   (`reported` / `converted-from-wt` / `method-default` / …). Record files are never modified by code
   paths other than explicit curation.
4. **Builds are pure and deterministic.** Every published file is a function of `data/`. A second
   `argus build` writes nothing.
5. **Every change since v1.0 is declared.** A row that differs from the frozen legacy rows must be listed in
   a curation-log entry (`rows_changed` / `rows_added` / `rows_removed`), or `argus verify` fails. Removed
   row ids are tombstoned and can never return.
6. **Open access only.** No Sci-Hub or paywall circumvention (policy entry in `data/exclusions.yaml`).

## 3. System overview

```mermaid
flowchart LR
  subgraph Acquire["Acquire (roadmap phase 6)"]
    D[Discovery<br/>OpenAlex · Crossref · Europe PMC]
    F[Full text<br/>EPMC JATS · Unpaywall · OA PDF]
    X[Extraction assist<br/>table parser · LLM + quote check · digitiser]
  end
  subgraph Curate["Curate (built)"]
    R[(data/records/*.yaml<br/>one file per paper)]
    S[(curation_log · exclusions<br/>tombstones · dataset.yaml)]
  end
  V{{argus validate<br/>21 rules}}
  B[argus build]
  subgraph Publish["Published outputs"]
    C[thermal_conductivity_dataset.csv<br/>+ inventory · log · uncertain · unusable]
    E[data/processed/measurements_enriched.csv]
    P[datapackage.json]
  end
  subgraph Analyse["Analyse"]
    PH[physics: EMT models + fits]
    BI[measurement-bias analysis<br/>mixed model + same-sample pairs]
    ML[ML: grouped-CV models<br/>(roadmap phase 5)]
    UI[Explorer<br/>(roadmap phase 7)]
  end
  Q{{argus verify<br/>release invariants}}
  D --> F --> X --> R
  R --> V --> B
  S --> B
  B --> C & E & P
  E --> PH & BI & ML & UI
  C & E & P --> Q
```

## 4. Repository layout

```
data/
  records/P001_10.3390_polym10030340.yaml   ← source of truth, one per paper (95)
  curation_log.yaml     pipeline-level log entries (bulk fixes); each declares rows it touched
  exclusions.yaml       screened sources that contribute no rows, with reasons
  tombstones.yaml       removed row ids (never reusable)
  dataset.yaml          dataset name, version, release date
  processed/            generated: rows.jsonl, measurements_enriched.csv
src/argus/
  schema.py     31-column row schema + record model (pydantic)
  records.py    load / save / compile record files
  validate.py   rule engine (errors block the build, waivers per row)
  units.py      k-unit parser and wt% ↔ vol% ↔ phr conversion
  vocab.py      method / direction / filler / matrix vocabularies
  reference/materials.yaml   densities and intrinsic k, each with source and `verified` flag
  enrich.py     analysis-ready table + QA summary
  package.py    Frictionless datapackage.json (spec v1)
  build.py      compile everything; refuses on errors
  verify.py     read-only release checks → reports/verification.json
  physics/emt.py  effective-medium models
  physics/fit.py  per-series model fitting
  analysis/lmm.py   REML random-intercept mixed model (between/within df)
  analysis/bias.py  measurement-technique and direction bias analysis
  ml/features.py    leakage-free feature matrix (27 columns, 10 groups)
  ml/models.py      baselines + learners (grouped inner tuning, monotone boosting)
  ml/benchmark.py   paper-grouped validation, conformal intervals, ablation
  ml/report.py      Markdown report, prediction table, parity plot
  fingerprint.py    dataset hash stamped into every analysis output
  report/course.py  course report rendered from results (refuses stale outputs)
  report/figures.py report figures (validated palette, small multiples)
  report/explorer.py interactive explorer: data payload + two page variants
  report/templates/ Jinja2 templates (course report, explorer head/body) and explorer.js
  legacy.py     one-time migration from work/ + change-declaration check
  cli.py        `argus` commands
tests/          pytest suite (unit, model identities, real-data invariants)
reports/        generated reports (verification, enrichment QA, physics fits)
docs/           this file, roadmap, research report and notes
work/           FROZEN legacy pipeline (v1.0); read-only reference
*.csv, README.md, FINAL_REPORT.md   published deliverables at the root (historical names kept)
```

## 5. Data model

### 5.1 Record file (`data/records/P###_<doi>.yaml`)

```yaml
schema_version: 1
paper_id: P001
paper: {doi: 10.3390/polym10030340, title: ..., year: 2018, source_url: https://doi.org/...}
extraction_log:            # how the paper was processed (seq = position in the chronological log)
- {seq: 1, candidate_id: P001, access_result: EPMC fullTextXML, tables_inspected: ..., ...}
measurements:
- row_id: b450fec2-001     # md5(doi)[:8]-NNN
  filler_material: h-BN
  filler_loading_vol_pct: 13.4
  k_composite_W_mK: 0.8
  k_original_value: 0.8
  k_original_unit: W/mK
  value_source: table      # text | table | figure
  source_location: Table 4 (k, measured vol%); Table 1 (wt%) sample ETLBN80-30
  confidence: High         # High | Medium
  waivers: []              # optional: [{rule: loading_present, reason: ...}]
```

Empty fields are omitted. Unknown keys are schema errors, so a typo such as `confidense:` cannot pass.

### 5.2 Published row (31 columns)

The 31-column layout of `thermal_conductivity_dataset.csv` is unchanged from v1.0 and is defined once in
`schema.COLUMNS` (name, type, unit, description). The CSV dialect is unchanged too (UTF-8 with BOM, CRLF,
minimal quoting), and the migration was verified byte-identical for all five deliverables.

### 5.3 Enriched table (31 + 25 columns)

`data/processed/measurements_enriched.csv` adds:

| Column(s) | Meaning | Basis column |
|---|---|---|
| `matrix_family`, `filler_family`, `filler_base`, `is_hybrid`, `contains_bn` | Normalised classes | — |
| `method_class`, `method_family`, `method_quantity` | Technique class (§6) | `method_basis`: named / generic / instrument / none |
| `direction_reported` | k_direction normalised | — |
| `direction_effective` | What was most likely sensed (incl. `mixed`) | `direction_basis`: reported / method-text / method-default / none |
| `phi_vol_pct`, `wt_pct_effective`, `rho_*_used` | Loading in both bases | `phi_basis`, `wt_basis` |
| `k_matrix_effective`, `k_enhancement` | Neat-matrix k, k/k_m | `k_matrix_basis`: reported / reference-default |
| `log10_k`, `k_rel_uncertainty` | Target transform; judgement-based method uncertainty | — |
| `flags` | Bias and provenance caveats (§6.2) | — |

Conversions use `reference/materials.yaml`. Each entry carries its source and a `verified` flag; only h-BN,
AlN and epoxy were verified in the research pass. **Self-check:** the 37 rows that report both wt% and vol%
for a single filler agree with the conversion to within 3.0 vol% (median 1.7). This check found the P094
designation-stored-as-wt% defect, and it is now a validator rule (`loading_basis_consistent`).

## 6. Measurement-technique vocabulary

### 6.1 Method classes

| Class | Family | Senses in a plate-like anisotropic sample | Default 1σ (if paper gives none) | Rows |
|---|---|---|---|---|
| `LFA` laser/xenon flash (ASTM E1461, ISO 22007-4) | transient, diffusivity | through-plane (standard holder) | 5% with Cp/ρ stated, else 8% | 72 |
| `THB` transient hot bridge | transient | mixed (≈ geometric mean) | 5% | 48 |
| `TPS` Hot Disk / transient plane source (ISO 22007-2) | transient | mixed (isotropic mode) | 5% | 28 |
| `HOT_WIRE` hot wire / needle / quick meter | transient | mixed | 6% | 12 |
| `SS_D5470` steady-state heat flow (ASTM D5470, DRL) | steady-state | through-plane, contact included | 10% | 8 |
| `PERIODIC` periodic heating / temperature wave | periodic | as reported | 8% | 4 |
| `SS_GHFM`, `SS_HFM_GHP`, `SS_UNSPECIFIED`, `MTPS`, `THIN_FILM`, `IR_THERMO` | — | see `vocab.METHOD_CLASSES` | 5–10% | 3 |
| `UNSPECIFIED` | — | unknown | 10% | 83 |

Rules are tiered. A **named** technique wins, and if several are named the first one mentioned wins
("Hot disk (this work); laser flash for literature rows" → TPS). Then a **generic** family name
("steady-state"), then an **instrument** model alone. Instrument names collide across techniques:
"TC-3000" is both a Sinku-Riko laser flash and a Xi'an Xiaxi hot wire, and Xiangyi's "quick meter" is a
TPS-type clone, while KEM's QTM is a hot wire. The uncertainty defaults are judgement values from the
research report (§Q4), not standard values.

### 6.2 Bias and provenance flags

| Flag | Rule | Rows |
|---|---|---|
| `mixed_direction_anisotropic` | Mixed-direction method on a BN-platelet sample | 82 |
| `contact_resistance_included` | Single-thickness steady-state rig | 10 |
| `lfa_cp_rho_unreported` | LFA where the method text does not say how Cp or ρ was obtained | 68 |
| `method_unspecified` | No technique named | 83 |
| `abstract_only`, `figure_digitized` | Provenance (both always Medium confidence) | 28, 28 |
| `matrix_prefilled`, `co_filler_ignored_in_conversion`, `non_ambient_temperature` | Interpretation caveats | 3, 2, 2 |

## 7. Validation rules

`argus validate` runs 21 rules. **Errors** block the build unless a row carries a reviewed waiver.

- **Identity:** `doi_format`, `paper_id_format`, `year_range`, `row_id_format` (prefix = md5(doi)), `row_id_unique`, `tombstone_reused`, `duplicate_measurement`.
- **Value:** `k_present_positive`, `k_unit_known`, `k_normalized_consistent` (original value × unit factor = normalised k).
- **Composition:** `loading_present`, `loading_range`.
- **Provenance policy:** `source_location_present`, `value_source_vocab`, `confidence_vocab`, `figure_not_high`, `abstract_not_high` (README convention: abstract-only rows start `Abstract (`).
- **Warnings:** `k_plausible`, `k_above_matrix`, `hybrid_label`, `loading_basis_consistent`.

`argus verify` adds release invariants:
- `outputs_in_sync`: all 8 generated files equal a fresh build.
- `exclusions_consistent`: no DOI is both excluded and present, unless its action says recovered.
- `papers_have_log`: every paper has an extraction-log entry.
- `figure_rows_cite_method`: figure-derived rows name the digitisation method.
- `waivers_justified`: every waiver carries a written reason.
- `changes_declared`: every difference from v1.0 is declared.

## 8. Physics module

`argus.physics.emt` implements the parallel/series and Hashin–Shtrikman bounds, Maxwell–Garnett,
Hasselman–Johnson, symmetric Bruggeman, differential (asymmetric) Bruggeman (with the Every et al. 1992
interface term), Lewis–Nielsen, Agari–Uno, the geometric mean, Foygel percolation and **Nan et al. 1997**.
Nan 1997 covers anisotropic spheroids with orientation ⟨cos²θ⟩ and interfacial resistance R_K. It
reproduces Maxwell and Hasselman–Johnson exactly as limiting cases, and the tests enforce this.

**Conventions** (the research report found papers that differ by 2× because of these):

| Quantity | Convention here | Trap |
|---|---|---|
| Loading | volume fraction φ ∈ [0, 1] | Percent input raises an error |
| Aspect ratio | p = t/D (< 1 for platelets) | Many papers quote D/t |
| R_K | Referenced to the particle **semi-axes**: γ = (1 + 2p)·R_K·k_m / a₃ | Yuan et al. 2016 use full thickness, so R_b(Yuan) = 2·R_K |
| Orientation | ⟨cos²θ⟩ of the platelet normal vs the measurement axis; 1/3 random | — |

The single γ expression above has the right limit in all three geometric cases: a sphere
(Hasselman–Johnson), a thin slab (series resistance through the thickness) and a long needle (a cylinder
with interface resistance). Model outputs match the research pass's independent calculations, and all of
these are regression tests.

`argus.physics.fit` groups rows into **loading series** (same paper and sample, varying loading; 17 series,
73 points, 9 papers) and fits one free parameter per model on log₁₀ k. First results
(`reports/physics_summary.json`):

- **98% of rows with a known loading (222/226) exceed the Maxwell ceiling** k/k_m = (1 + 2φ)/(1 − φ).
  That is the kf → ∞ limit, so no isolated-sphere model can describe these composites. The Maxwell fit hit
  its parameter bound in all 17 series (median RMSE 0.30 in log₁₀, about a factor of 2).
- Lewis–Nielsen with k_f fixed to the intrinsic value fits with median shape factor A = 13.6 (IQR 6–22).
  Median RMSE is 0.044 in log₁₀ (about 11%).
- Apparent R_K from Nan 1997 (random orientation, assumed geometry) has a median of 6.8×10⁻⁷ m²K/W
  (IQR 2.5×10⁻⁷–1.05×10⁻⁶). That is inside the published BN/epoxy range. In 7 of 17 series the data exceed
  even the perfect-interface prediction, which points to alignment or percolating networks.
- Agari–Uno has the lowest RMSE but two free parameters, so it is favoured by construction on 3–5-point
  series.

Fitted parameters are **apparent**: they absorb voids, dispersion and measurement-direction effects. They
are diagnostics for comparing papers, not interface physics.

## 8a. Measurement-bias analysis

`argus analyze bias` (`src/argus/analysis/`) asks how much the measurement technique and direction shift
reported k. It weighs three kinds of evidence, strongest first:

1. **Same-sample pairs**: rows identical in paper, composition, processing and loading but reported in two
   directions or by two methods.
2. **Anisotropy → method bias**: an isotropic-mode TPS/THB/hot-wire sensor reads about √(k_in·k_through),
   i.e. √A times the laser-flash through-plane value.
3. **Pooled between-paper model**: log₁₀(k/k_m) ~ φ + φ² + BNNS + in-plane + method group, with a random
   intercept per paper.
   - The mixed model (`lmm.py`) is a small REML implementation, tested against dense-matrix algebra.
   - It uses between/within degrees of freedom: method is constant within a paper, so its interval is judged
     against the number of papers, not rows.

Results are in [`reports/method_bias.md`](../reports/method_bias.md) and summarised in the
[roadmap](ROADMAP.md#phase-4-measurement-bias-analysis--course-centrepiece). In short, same-sample anisotropy
(median A = 6.7) implies up to 2.8× method-dependent differences. The between-paper method contrast is
1.43× (CI 0.86–2.36), and no sample was measured by two techniques.

## 8b. Machine learning

`argus ml benchmark` (`src/argus/ml/`) asks whether composition, processing and method metadata predict k
for a paper the model has never seen.

- **Features** (`features.py`): 27 columns in 10 named groups. Every feature is a fixed row-wise function of
  the enriched row, so building them cannot leak information between folds. Missing sizes use a fixed
  constant plus an indicator, not a dataset median. The target is log₁₀(k/k_m).
- **Models** (`models.py`): three baselines (median, calibrated Nan 1997, nearest neighbours) and four
  learners:
  - ridge, with alpha chosen by an inner split that also keeps papers together;
  - calibrated physics plus a Gaussian process on the residuals;
  - gradient boosting, constrained to be non-decreasing in every loading-derived feature;
  - a random forest.
- **Validation** (`benchmark.py`):
  - Leave-one-paper-out is the headline, alongside repeated 5-fold by paper.
  - Row-level 5-fold is reported only as a leakage contrast.
  - A time split and leave-one-filler-family-out test extrapolation.
  - Intervals are paper-grouped conformal: each held-out paper's interval comes from the other papers'
    residuals.
  - The ablation removes feature groups (and overlapping pairs) on identical splits, so the differences are
    paired.

Headline: ×1.66 typical error on an unseen paper (gradient boosting) against ×1.91 and ×2.14 for the best
baselines. Calibrated 90% intervals are ×/÷3.4 wide. Details are in [`reports/ml_benchmark.md`](../reports/ml_benchmark.md).

## 9. Testing

`pytest` covers:
- the unit parser (every unit string in the data, prefixes, rejected look-alikes);
- each validation rule and waivers;
- record round-trips and build determinism (a blocked build writes nothing);
- vocabulary classification of real strings and enrichment bases;
- model limits, bounds and identities, plus the research cross-check numbers;
- parameter recovery from synthetic series;
- real-data invariants (validation clean, outputs in sync, every change since v1.0 declared, fresh migration
  lossless).

Because `argus verify` compares generated files byte-for-byte, `.gitattributes` pins their line endings
(CSV → CRLF, JSON/JSONL → LF). That way a fresh clone verifies on Windows and Linux regardless of
`core.autocrlf`. CI (`.github/workflows/ci.yml`) runs `argus validate`, `pytest` and `argus verify` on
every pull request and every push to `main`.

Commands:

```bash
python -m pytest
```

```bash
python -m argus verify
```

## 10. Key decisions

| Decision | Alternatives | Why |
|---|---|---|
| YAML file per paper as the source of truth | SQLite / one big JSONL | Human review in diffs; one paper = one change; no server |
| Keep the 31-column CSV and its dialect | Redesign the schema | Downstream users and the v1.0 report stay valid; migration provable byte-for-byte |
| Derived columns in a separate enriched table | Fill blanks in place | Keeps "printed in the paper" separate from "computed by us" |
| Frictionless descriptor at spec v1 | v2 (2024) | v2 readers were not available in Python/R as of early 2026 |
| `mixed` as a direction value | Force in-plane/through-plane | Isotropic-mode TPS/THB/hot-wire report a mixture on anisotropic samples |
| Semi-axis R_K convention | Full thickness | Consistent with Nan 1997 and all physical limits; the convention is stored with every fit |
| No Sci-Hub | — | Copyright; the dataset must be redistributable |
