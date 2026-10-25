# External datasets

Data curated by other groups, used to **test** ARGUS: its physics code, its models and its extracted values.
Nothing here enters `data/records/` or the published ARGUS tables. Run everything with:

```bash
pip install -e ".[ml,report,external]"
```

```bash
argus external fetch
```

```bash
argus external validate
```

`argus external fetch` downloads the raw files that are not committed (see licences) and checks every
file's sha256 against `sources.yaml`; `argus verify` fails if a committed raw file changes.
`argus external validate` writes `reports/external_validation.md` and `.json`.

| Folder | Source | Licence | In git | Used for |
|---|---|---|---|---|
| `evf/` | Anastasiou, *EVF_Thermal_Conductivity_Dataset*, figshare 2026, [10.6084/m9.figshare.31408854.v1](https://doi.org/10.6084/m9.figshare.31408854.v1) | CC BY 4.0 | raw workbook + README | Independent test set (polymer + ceramic series only, see `evf/series_map.yaml`); physics-code cross-check |
| `bcc/` | He, Wu & Fu, source data of *Nat. Commun.* 2025, figshare, [10.6084/m9.figshare.30426895.v1](https://doi.org/10.6084/m9.figshare.30426895.v1) | MIT | raw workbook + README | Physics-code cross-check and effective-medium accuracy at high loading (no material names per row) |
| `ncomms/` | He, Wu & Fu, *Nat. Commun.* 2025, Supplementary Data 1, [10.1038/s41467-025-67013-y](https://doi.org/10.1038/s41467-025-67013-y) | CC BY-NC-ND 4.0 | **no** (fetched on demand); our block map is | Second independent test set; value cross-check |
| `tagp/` | Sarikhani et al., *Appl. Phys. Rev.* 9, 041403 (2022), S10, [arXiv 2209.07635](https://arxiv.org/abs/2209.07635) | CC BY 4.0 | our transcription of DS03 and DS04 (PDF fetched on demand) | Test set (DS03) and value cross-check (DS04) |
| `heliyon/` | Mumtaz et al., *Heliyon* 10, e25381 (2024), Table 1, [10.1016/j.heliyon.2024.e25381](https://doi.org/10.1016/j.heliyon.2024.e25381) | CC BY-NC-ND 4.0 | only the 2 rows whose papers are in ARGUS, as facts with attribution | Value cross-check |

**Changes we made** (CC BY requires saying so): we selected series/blocks, normalized filler and matrix
labels, resolved source DOIs (Crossref) and mapped the Nature Communications blocks to their papers using
the article's Supplementary Table S3. Every choice is recorded next to the data: `evf/series_map.yaml`,
`ncomms/block_map.yaml`, the TAGP and Heliyon CSVs, and `crosscheck_review.yaml` for the hand review of
papers that ARGUS shares with an external source. No measured value was altered.

**Rules the code enforces**

- A raw file whose sha256 differs from `sources.yaml` fails `argus external check` and `argus verify`.
  The two committed transcriptions (`tagp/tagp_thermal_datasets.csv`, `heliyon/shared_rows.csv`) are pinned
  the same way.
- One DOI is one paper: a DOI may be split into several paper groups only when every record of it carries
  an explicit group (a declared compilation, such as the Machrafi 2016 series in EVF). Anything else is an
  error, because it would put one paper on both sides of a leave-one-paper-out split.
- Every EVF series and every Nature Communications block must be listed as included or excluded (with a
  reason); an unmapped series or a block map that does not tile the workbook is an error.
- External rows from a paper that ARGUS also contains are never test rows (the leakage guard moves them
  to the value cross-check), and a paper present in two test sets is counted once.
- The model-prediction columns in the EVF and BCC workbooks are only used to check our physics code;
  they are never model inputs.
