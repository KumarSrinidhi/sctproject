# Dataset licence

**ARGUS: Source-verified thermal conductivity of BN- and AlN-filled polymer composites**, version 1.2.0
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
  publishers' licences, all of them CC BY; `work/THIRD_PARTY.csv` lists each file with its evidence.
  - Of the 70 stored full texts (`*.txt`), 36 state a CC BY licence: 35 give version 4.0 and one MDPI paper
    gives no version.
  - The other 34 do not state a licence in the extracted text. Crossref records a CC BY licence for each
    of them.
  - On 2026-10-25, 22 files without clear redistribution rights were taken out of the repository:
    - 8 non-commercial (CC BY-NC);
    - 11 with no open licence found in the text or on Crossref;
    - 3 saved captcha pages.

    They are kept only in the git-ignored `local_archive/` folder of the working copy, with
    `local_archive/third_party/MOVED.csv` listing each one and why. No dataset value depends on them,
    because every row cites its DOI and quotes its source.
- **External datasets.** `data/external/` holds other groups' datasets used to test ARGUS. They keep their
  own licences, listed in `data/external/sources.yaml` and `data/external/README.md`: EVF (CC BY 4.0),
  the BCC source data (MIT), and our transcriptions from Sarikhani et al. 2022 (CC BY 4.0). Two sources
  are CC BY-NC-ND 4.0 (He et al. 2025 Supplementary Data 1, Mumtaz et al. 2024): their files are not
  redistributed here. `argus external fetch` downloads them, and only our own curation (block map,
  two rows of facts with attribution) is committed. Our mapping files in `data/external/` are CC BY 4.0
  like the rest of the dataset.
- **Explorer pages.** `docs/explorer/index.html` and `docs/explorer/explorer.artifact.html` embed an
  optional "other groups' data" layer: points from EVF (Anastasiou 2026) and from Sarikhani et al. 2022.
  Those points keep their sources' CC BY 4.0 licences, with the attribution given in the page footer and in
  `data/external/sources.yaml`. Only the ARGUS records in those pages are licensed by this file.
- **Quoted excerpts.** The `source_location` and `notes` columns quote short passages from the source papers
  to make every value traceable. Those passages remain the work of their original authors.
  - The measured values themselves are facts reported by those papers.
  - When you reuse a value, cite its source paper (the DOI is in every row) as well as this dataset.

## Before making the repository public

1. ~~Remove third-party files whose licence does not allow redistribution.~~ Done on 2026-10-25: every
   remaining file is CC BY (`work/THIRD_PARTY.csv`, checked by `pytest`).
2. ~~Delete the three saved captcha pages~~, which embedded the IP address of the machine that fetched
   them. Done on 2026-10-25.
3. **Still to do:** the removed files are still in the git history. Publish from a fresh repository (a
   single snapshot commit of `main`), or rewrite this repository's history, so they are really gone.

## How to cite

> Kumar, A., & Reddy, R. K. S. (2026). ARGUS: Source-verified thermal conductivity of BN- and AlN-filled polymer composites (Version 1.2.0) [Data set]. https://github.com/KumarSrinidhi/sctproject

Machine-readable citation metadata is in `CITATION.cff`; GitHub shows it under "Cite this repository".

## No warranty

The dataset is provided as is. Values were transcribed or digitized from the cited sources and checked
against them, but check a value against its source before using it in a publication, a design or a
regulatory context.
