# Polymer–Ceramic Thermal Conductivity Dataset (ARGUS)

**Source-verified experimental measurements of effective thermal conductivity (k) for polymer–ceramic composites, with primary focus on epoxy + h-BN/BNNS/AlN** — the electrically insulating, thermally conductive materials used for semiconductor packaging and thermal interface materials.

All values are traceable to a specific paper, table, figure, or text location. No value is estimated, back-calculated or model-predicted; literature-comparison values are excluded. Figure-derived values are pixel-digitized with a reproducible script and flagged `value_source=figure`, `confidence=Medium`.

**Dataset v1.1.0** (released 2026-10-23, tag `data-v1.1`): **258 rows / 95 papers**. See [data/CHANGELOG.md](data/CHANGELOG.md) for what changed since v1.0 (260 rows).

| Document | What it covers |
|---|---|
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | How the dataset and toolkit are built: data model, validation, measurement-method vocabulary, physics models |
| [docs/ROADMAP.md](docs/ROADMAP.md) | Phases, status and acceptance criteria |
| [docs/reports/BN epoxy thermal conductivity research.md](docs/reports/BN%20epoxy%20thermal%20conductivity%20research.md) | Research report: characterization techniques and their biases, effective-medium models, ML prior work, tooling |
| [FINAL_REPORT.md](FINAL_REPORT.md) | v1.0 presentation report (historical) |

---

## Quickstart (toolkit)

Python 3.10+. Dependencies: pydantic, pyyaml, numpy, pandas, scipy, typer (and pytest for tests).

```bash
pip install -e ".[dev]"
```

```bash
argus validate
```

```bash
argus build
```

```bash
argus verify
```

Without installing, run from the repo root with `PYTHONPATH=src python -m argus <command>`.

| Command | Does |
|---|---|
| `argus validate` | Checks every record against 21 rules (errors block the build) |
| `argus build` | Compiles `data/records/` into all published files; writes nothing if there are errors |
| `argus verify` | Read-only release checks → `reports/verification.json` |
| `argus stats` | Headline numbers |
| `argus physics` | Fits effective-medium models to every loading series → `reports/physics_*` |
| `argus analyze bias` | How much measurement technique and direction shift k → `reports/method_bias.md` |
| `argus ml benchmark` | Predict k for unseen papers; baselines vs models, honest validation → `reports/ml_benchmark.md` (needs the `ml` extra: `pip install -e ".[ml]"`) |
| `argus report course` | Render the course report [docs/course_report/COURSE_REPORT.md](docs/course_report/COURSE_REPORT.md) and its figures from current results (needs the `report` extra; refuses stale analysis outputs) |
| `argus report explorer` | Render the interactive data explorer `docs/explorer/index.html`, a self-contained page you can open in any browser, plus a variant for publishing as a shared link |
| `argus new-paper --doi … --title … --year …` | Creates a record file for a new paper |

**Adding or correcting data:** edit (or create) the paper's file in `data/records/`, then run `argus validate` and `argus build`. If you change existing rows, add an entry to `data/curation_log.yaml` listing the row ids under `rows_changed` / `rows_removed`; `argus verify` fails on undeclared changes. Removed row ids go in `data/tombstones.yaml`.

---

## Deliverables

| File | Contents |
|---|---|
| `thermal_conductivity_dataset.csv` | 258 rows / 95 papers, 31 columns (full schema below) |
| `data/processed/measurements_enriched.csv` | Same rows + 25 derived columns (method class, effective direction, vol% from wt%, bias flags), each with a `*_basis` column |
| `datapackage.json` | Frictionless Data Package descriptor (types, units, descriptions) |
| `paper_inventory.csv` | 95 papers with row counts, fillers, matrices, k ranges |
| `extraction_log.csv` | Per-paper and per-pass audit trail (107 entries) |
| `uncertain_measurements.csv` | 64 Medium-confidence rows (28 abstract-only + 28 figure-digitized + 8 earlier) |
| `unusable_sources.csv` | 51 screened sources that contribute no rows, with reasons (incl. the Sci-Hub policy note) |
| `data/records/` | **Source of truth**: one YAML file per paper |
| `reports/` | Verification, enrichment QA and physics-fit reports (generated) |
| `quality_control_report.md`, `FINAL_REPORT.md`, `figures/` | v1.0 QC report, presentation report and charts (historical) |

---

## Schema (`thermal_conductivity_dataset.csv`)

Key columns (types, units and descriptions for every column are in `datapackage.json`):

- `row_id`, `doi`, `source_url`, `paper_title`, `year`
- `matrix_polymer`, `curing_agent`
- `filler_material` (normalized: h-BN / BN / BNNS / AlN / cBN / `<a>/<b> hybrid`), `filler_material_original` (verbatim from source)
- `filler_shape`, `filler_aspect_ratio`, `filler_mean_size_um`, `functionalization`, `filler_alignment`
- `filler_loading_vol_pct`, `filler_loading_wt_pct` (filler mass fraction of the whole composite), `filler_loading_original_value`, `filler_loading_original_unit`
- `processing_method`
- `k_matrix_W_mK`, `k_composite_W_mK` (normalized to W/m·K), `k_direction`
- `measurement_method`, `measurement_temperature_C`
- `k_original_value`, `k_original_unit` (as printed in source)
- `value_source` (text / table / figure), `source_location` (verbatim quote, table ID, or figure + series + digitizer reference)
- `confidence` (High / Medium)
- `notes` (hybrid composition, optional-matrix flags, caveats)

---

## Scope

**Primary (epoxy + BN/AlN):** 228 epoxy-based rows; h-BN (85) + BN (54) + BNNS (53) + AlN (20) = 212 single-filler BN/AlN rows.

**Optional matrices:** silicone incl. PDMS (16), polyimide (9), PEG PCM (2), polystyrene (2), polyurethane (1).

**Hybrid fillers retained:** Al2O3/BN, h-BN/AlN, h-BN/cBN, BN/graphene, BN+CNT, BNNS/MWCNTs@mSiO2, 3D BN/PA66 scaffold, etc. `filler_material` contains "hybrid"; composition detail is in `notes`.

**Excluded:** reviews, modeling-only papers and model-predicted values, literature-comparison values, values only given relative to another sample, carbon-only fillers, metal hybrids (e.g. Ag-bridged BNNS), Si3N4-only and PCM (paraffin/LA-ODE) matrices. Figure-only values are included only when pixel-digitized with `work/phase4_digitize_v2.py` (2 papers so far).

---

## Data characteristics

- **k range:** 0.17 – 47.03 W/m·K (median 1.035; the high tail is in-plane anisotropic BNNS networks at 60 wt%)
- **Year range:** 1997 – 2026
- **Temperature:** ambient (~25 °C) unless `measurement_temperature_C` is set (e.g., a 77 K cryogenic row)
- **Direction:** `k_direction` = through-plane / in-plane / unknown as reported. The enriched table adds `direction_effective`: isotropic-mode Hot Disk, hot-bridge and hot-wire values on BN-platelet samples are `mixed` (≈ geometric mean of in-plane and through-plane), and laser flash on a disc is through-plane.
- **Measurement method:** laser flash 72 rows, transient hot bridge 48, Hot Disk/TPS 28, hot wire 12, steady-state D5470-type 8, other 7, not stated 83 (`method_class` in the enriched table).
- **Unit normalization:** all k converted to W/m·K; original units preserved and the conversion is re-checked on every build.

---

## Extraction methodology

1. **Discovery:** Crossref + Semantic Scholar + Europe PMC + OpenAlex searches (polymer/epoxy/BN/AlN/h-BN/BNNS + thermal conductivity).
2. **Triage:** abstract screening for experimental composite k values.
3. **Full-text retrieval:** Europe PMC fullTextXML (open access), ChemRxiv, Unpaywall, OA repositories. Publisher HTML blocked (403) for Wiley/Elsevier/Springer/IOP/ACS is listed in `unusable_sources.csv`. Phase 3 added Semantic Scholar abstract harvest for still-blocked papers.
4. **Extraction:** per-paper scripts (`work/extract_001.py` … `extract_027.py`, v1.0) parsed text and tables; every row carries `source_location`. Abstract-only rows are `confidence=Medium` with `source_location` prefixed `Abstract (...)`.
5. **Figures:** browser-fetched OA full texts upgraded 4 abstract-only rows to High; 2 figure-only papers were pixel-digitized (`work/phase4_digitize_v2.py`, overlays in `work/figures/`).
6. **Curation (v1.1+):** the v1.0 rows were migrated losslessly into `data/records/`. All changes since then are made in those files, validated by `argus validate`, and declared in `data/curation_log.yaml`.
7. **QC:** `argus verify` (release invariants) and `pytest` (unit, physics and real-data tests). Phase 1–4 audit history: `audit_phase1_report.md`, `quality_control_report.md`, `work/*_verification.json`.

The v1.0 scripts, full texts and logs are kept unchanged in `work/` for reproducibility; that folder is frozen.

---

## How to cite a value

Every row is independently traceable:

```
row_id, doi, source_location
e.g. "bf4f3fd7-042", "10.3390/polym13060955", "Table 2, EP/BN 30 wt%: 0.85 W/(m·K)"
```

Cross-check `source_location` against the paper before using a value in a publication.

---

## Gaps / future work

See [docs/ROADMAP.md](docs/ROADMAP.md). In short:
- About 200 Wiley/Elsevier/Springer/IOP papers are still blocked; recoverable only via OA manuscripts and repositories.
- 28 rows are abstract-only (Medium). Full text would confirm matrix, curing agent and measurement method.
- More figure-only series can be digitized the same way (polym10030277, polym11101548, polym15051214, ma18215011 Fig. 5a).
- 83 rows do not name the measurement technique; 56 of them come from papers whose full text is available.

---

## Citation

> Kumar, A., & Reddy, R. K. S. (2026). ARGUS: Source-verified thermal conductivity of polymer-ceramic composites (epoxy + BN/AlN) (Version 1.1.0) [Data set]. https://github.com/KumarSrinidhi/sctproject

`CITATION.cff` holds the machine-readable version (GitHub shows it under "Cite this repository"). When you reuse an individual value, also cite its source paper; the DOI is in every row.

---

## License

- **Code:** [MIT](LICENSE). This covers `src/`, `tests/`, the Python scripts in `work/`, `pyproject.toml` and `.github/`.
- **Data:** [CC BY 4.0](LICENSE-DATA.md). This covers everything else in the repository: the published tables, `data/`, `reports/`, the documents in `docs/`, the earlier reports and figures at the root, and the legacy logs and backups. `LICENSE-DATA.md` has the full list.
- **Third-party papers** stored in `work/fulltext/`, `work/phase4_browser/` and `work/figures/` keep their publishers' licences; two are non-commercial (CC BY-NC). Work through the checklist in `LICENSE-DATA.md` before making the repository public.

Values were extracted from open-access papers only; Sci-Hub was deliberately not used. Check a value against its source before commercial or regulatory use.
