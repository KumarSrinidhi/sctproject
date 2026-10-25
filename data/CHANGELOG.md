# Dataset changelog

Versioning: `major.minor.patch` in `data/dataset.yaml`. Minor = rows added/removed or values corrected.
Every row-level change is also declared in `data/curation_log.yaml` (`rows_changed` / `rows_removed`), and
`argus verify` fails if a difference from v1.0 is not declared.

## 1.2.0 (2026-10-25): Phase 6 acquisition

**639 rows / 174 papers** (v1.1: 258 / 95). Confidence 552 High / 87 Medium. Value source 442 text /
169 table / 28 figure. k range 0.12–50.0 W/(m·K), median 1.10.

Added: 381 rows from 79 new open-access papers (records P096–P176; P135 and P173 were created and
removed in the same pass). See `data/acquisition/` and `docs/ARCHITECTURE.md` §8d.
- **Discovery:** OpenAlex queries, all logged in `queries.jsonl`; 663 DOIs, 251 screened in.
- **Full text:** Europe PMC JATS for 100 of them.
- **Extraction and checking:**
  - Values printed in text or tables only; figure-only values were counted, not digitized.
  - One agent extracted and a second, independent agent checked every row against the source: 406
    candidate rows, 0 rejected, 71 descriptive fields corrected, 2 missed rows added.
  - On import, every quote was re-checked as verbatim and as containing the printed k.
- **Post-import review** resolved 78 validation problems and applied the README scope rules. 25 rows
  were dropped before release and tombstoned:
  - the loading was not printed;
  - the unit was not a conductivity;
  - the authors had excluded the run;
  - metal-hybrid fillers (Ag, low-melting alloy);
  - a paraffin-type phase-change matrix.

  In addition:
  - 4 neat-matrix rows were given a 0 wt% loading;
  - 29 printed unit typos were recorded as W/(m·K), with the printed form in notes.
- **House rule:** values printed as approximate or as a bound are Medium confidence.

Exclusions: 51 → 72. 19 screened-in papers had no usable printed values (reviews, simulation-only,
non-polymer matrices, figure-only or relative values); 2 records were emptied by the review.

ML benchmark (leave-one-paper-out, ensemble): MAE 0.236 log₁₀ (×1.72) on 377 single-filler rows from 119
papers; v1.1 gave 0.223 (×1.67) on 218 rows from 80 papers. Calibrated physics: ×2.06.

The scope widens with the data, so the dataset title becomes "BN- and AlN-filled polymer composites".
Epoxy is still the most common matrix (271 rows), followed by silicone (119) and polyethylene (74). The
matrix vocabulary gains thermoplastic families with handbook reference values, marked unverified.

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
