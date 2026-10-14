import sys, re
sys.stdout.reconfigure(encoding="utf-8")
readme = open("README.md", encoding="utf-8").read()
qc = open("quality_control_report.md", encoding="utf-8").read()
anchors_r = [
 "188 rows / 63 papers",
 "(70 entries)",
 "9 Medium-confidence rows",
 "- **k range:** 0.17 \u2013 19.0 W/m\u00b7K (median 1.052)",
 "- **Year range:** 1997 \u2013 2026",
]
anchors_q = [
 "| Total rows | 188 |",
 "| Unique papers | 63 |",
 "| Year range | 1997\u20132026 |",
 "| k_composite range | 0.17 \u2013 19.0 W/m\u00b7K |",
 "| Median k | 1.052 W/m\u00b7K |",
 "**Generated:** 2026-10-13",
 "## 2. Validation checks (all passed)",
 "- **k_composite_W_mK:** all 188 values numeric, positive, in range 0.17\u201319.0 (no zeros, no negatives, no NaN).",
 "- **filler_loading:** vol_pct, wt_pct, or original_value present for all rows (validation rule: at least one).",
 "9 rows marked Medium confidence (listed in `uncertain_measurements.csv`). Typical reasons:",
 "1. Filter `confidence == 'High'` for primary analysis (179 rows).",
 "2. Epoxy + BN-family subset (h-BN + BN + BNNS = 149 rows) is the core target scope.",
 "3. Optional matrices (silicone, PI, PDMS, PEG, PS, PU, LC epoxy = 30 rows) are tagged; filter out if strictly epoxy-only is needed.",
 "### By matrix polymer (top)",
 "\n---\n\n## 2.",
]
bad = []
for a in anchors_r:
    if a not in readme: bad.append(("README", a[:80]))
for a in anchors_q:
    if a not in qc: bad.append(("QC", a[:80]))
print("MISSING:" if bad else "ALL ANCHORS OK")
for b in bad: print("  ", b)
