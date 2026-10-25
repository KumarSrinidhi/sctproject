# Dataset licence

**ARGUS: Source-verified thermal conductivity of polymer-ceramic composites (epoxy + BN/AlN)**, version 1.1.0
© 2026 Aniket Kumar and Rao Kumar Srinidhi Reddy

The dataset is licensed under the **Creative Commons Attribution 4.0 International licence (CC BY 4.0)**.
Summary: https://creativecommons.org/licenses/by/4.0/ · Legal code: https://creativecommons.org/licenses/by/4.0/legalcode

You may share and adapt the dataset for any purpose, including commercially, provided you give appropriate
credit, link to the licence, and indicate if you made changes.

## Which licence covers which file

- **MIT** (see `LICENSE`) covers the source code and its configuration: `src/`, `tests/`, the Python scripts
  in `work/`, `pyproject.toml` and `.github/`.
- **Third-party material** is not ours to license; it is listed in the next section.
- **CC BY 4.0** covers everything else in this repository. That includes:
  - the published tables (`thermal_conductivity_dataset.csv`, `paper_inventory.csv`, `extraction_log.csv`,
    `uncertain_measurements.csv`, `unusable_sources.csv`) and `datapackage.json`;
  - `data/` (records, curation log, exclusions, tombstones, processed tables) and `reports/`;
  - the documents in `docs/` (course report, research report and notes, explorer pages);
  - the earlier reports and charts at the root (`FINAL_REPORT.md`, `quality_control_report.md`,
    `audit_phase1_report.md`, `figures/`);
  - the legacy logs, JSON outputs and backups in `work/` and `backup_phase2/`.

**Archived snapshots.** `backup_phase2/` and everything in `work/` whose name starts with `backup_` (folders and files such as `work/backup_phase1_README.md`) are frozen copies of earlier deliverables. The
licence wording in their README files (for example "CC-BY, CC-BY-SA, etc." or "for research use") is
historical and superseded by this file.

## What it does not cover

- **Third-party papers.** `work/fulltext/`, `work/phase4_browser/` and `work/figures/` contain copies or
  excerpts of the source papers and their figures, kept for reproducibility. They remain under their
  publishers' licences.
  - Of the 83 stored full texts (`*.txt`), 36 state a CC BY licence: 35 give version 4.0 and one MDPI paper
    gives no version.
  - Two state **non-commercial** licences: `10.1177_09673911221110143` (CC BY-NC 4.0) and
    `10.3740_mrsk.2023.33.12.503` (CC BY-NC 3.0).
  - The other 45 do not state a licence in the extracted text.
- **External datasets.** `data/external/` holds other groups' datasets used to test ARGUS. They keep their
  own licences, listed in `data/external/sources.yaml` and `data/external/README.md`: EVF (CC BY 4.0),
  the BCC source data (MIT), and our transcriptions from Sarikhani et al. 2022 (CC BY 4.0). Two sources
  are CC BY-NC-ND 4.0 (He et al. 2025 Supplementary Data 1, Mumtaz et al. 2024): their files are not
  redistributed here. `argus external fetch` downloads them, and only our own curation (block map,
  two rows of facts with attribution) is committed. Our mapping files in `data/external/` are CC BY 4.0
  like the rest of the dataset.
- **Quoted excerpts.** The `source_location` and `notes` columns quote short passages from the source papers
  to make every value traceable. Those passages remain the work of their original authors.
  - The measured values themselves are facts reported by those papers.
  - When you reuse a value, cite its source paper (the DOI is in every row) as well as this dataset.

## Before making the repository public

1. Review `work/fulltext/`, `work/phase4_browser/` and `work/figures/`.
   - Remove anything whose licence does not allow redistribution, starting with the two non-commercial
     papers and the 45 with no stated licence.
2. Delete the three saved captcha pages:
   - `work/fulltext/10.1088_1361-6528_ac0470.pdf`
   - `work/fulltext/10.1088_1742-6596_1003_1_012082.pdf`
   - `work/fulltext/10.1088_1757-899x_274_1_012043.pdf`

   They are HTML bot-check pages, not papers, and they embed the IP address of the machine that fetched them.
3. Deleting files does not remove them from git history. Publish from a fresh repository, or rewrite the
   history, so that the removed files are really gone.

## How to cite

> Kumar, A., & Reddy, R. K. S. (2026). ARGUS: Source-verified thermal conductivity of polymer-ceramic composites (epoxy + BN/AlN) (Version 1.1.0) [Data set]. https://github.com/KumarSrinidhi/sctproject

Machine-readable citation metadata is in `CITATION.cff`; GitHub shows it under "Cite this repository".

## No warranty

The dataset is provided as is. Values were transcribed or digitized from the cited sources and checked
against them, but check a value against its source before using it in a publication, a design or a
regulatory context.
