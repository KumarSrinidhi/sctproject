# Dataset changelog

Versioning: `major.minor.patch` in `data/dataset.yaml`. Minor = rows added/removed or values corrected.
Every row-level change is also declared in `data/curation_log.yaml` (`rows_changed` / `rows_removed`), and
`argus verify` fails if a difference from v1.0 is not declared.

## 1.1.0 (2026-10-23): close open audit items

**258 rows / 95 papers** (v1.0: 260 / 95). Confidence 194 High / 64 Medium. Value source 158 text /
72 table / 28 figure. k range 0.17–47.03 W/(m·K), median 1.035.

Removed (tombstoned in `data/tombstones.yaml`):
- `b639a9c9-159`: 30 wt% AlN, k = 1.052 (10.3390/ma18215011). Not printed in the paper; it was
  back-calculated from "1.278 W/m·K … 21.4% … increase compared to the … AlN" composite (audit D7).
- `ce78048d-168`: in-plane k = 1.88 (10.3390/nano11081898). The paper's own parallel-model **prediction**,
  not a measurement.

Corrected:
- `c027d8f9-233…243` (P094, 10.3390/polym11071156): `filler_loading_wt_pct` held the sample designation
  (BN per epoxy+BN) instead of the composite mass fraction. Recomputed from the paper's Table 1 parts
  (epoxy/BN/thiol/LC-80): 30 → 20.2, 50 → 37.2, 60 → 46.9, 70 → 58.0 wt%. vol% and k are unchanged. The
  enrichment density check found this; it is the same defect class as audit D2.
- `b639a9c9-160/161`: `BN` → `h-BN/AlN hybrid`. `7239d84d-165/166`: `h-BN` → `h-BN/cBN hybrid`
  (README hybrid convention).
- `b639a9c9-161`: `source_location` now quotes the sentence verbatim. The old text attributed the 25.2% to
  AlN, but it refers to Al₂O₃.

Exclusions (`unusable_sources.csv`, 49 → 51 entries):
- Added `10.3390/polym11101548` and `10.3390/polym15051214`. Both were screened but never logged (audit
  D10); their own k values are relative-only in the text.
- `10.3390/polym10030277` and `10.1039/c8ra10645b` are marked *recovered*. They had rows since Phase 3A
  but were still listed as excluded.

Tooling: the dataset is now built by `argus build` from `data/records/` (see `docs/ARCHITECTURE.md`). The
v1.0 deliverables were reproduced byte-for-byte before these changes were applied.

Data corrections were made on 2026-10-22. Release (tag `data-v1.1`, 2026-10-23): added citation metadata (`CITATION.cff`, generated from
`data/dataset.yaml`), the data licence (CC BY 4.0, `LICENSE-DATA.md`) and the code licence (MIT, `LICENSE`).
Authors: Aniket Kumar and Rao Kumar Srinidhi Reddy. No data values changed, so the dataset fingerprint is
still `12ef8fe97057dafc`.

## 1.0.0 (2026-10-18): Phase 4 final

260 rows / 95 papers. See `FINAL_REPORT.md` and `quality_control_report.md`.
