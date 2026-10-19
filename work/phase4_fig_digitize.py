"""Phase 4 Mission B: figure-digitized k values (digitized from PMC figure images
downloaded via browser CDN; max 3 sig figs; reading uncertainty ~ +/-0.05 W/mK)."""
import json, os

DATA = {
  "10.3390/polym11071156": {
    "source": "Figure 11 (polymers-11-01156-g011.jpg via PMC CDN, browser-fetched)",
    "method": "visual digitization, max 3 sig figs",
    "note": "paper text contains no k values; table 1 gives BN wt% (10/30/50/60/70); paper text gives vol% for ETLBNx-30=12.9, -50=25.7, -60=34.2, -70=44.7; EJBN30 x-positions digitized",
    "points": [
      {"x": "0.0", "k": 0.22, "system": "ETL (neat epoxy-thiol, baseline for all ETLBNx)"},
      {"x": "12.9", "k": 0.98, "system": "ETLBN180-30"},
      {"x": "25.7", "k": 1.97, "system": "ETLBN180-50"},
      {"x": "34.2", "k": 3.02, "system": "ETLBN180-60"},
      {"x": "44.7", "k": 4.21, "system": "ETLBN180-70"},
      {"x": "12.9", "k": 0.75, "system": "ETLBN30-30"},
      {"x": "25.7", "k": 1.61, "system": "ETLBN30-50"},
      {"x": "34.2", "k": 2.33, "system": "ETLBN30-60"},
      {"x": "44.7", "k": 3.34, "system": "ETLBN30-70"},
      {"x": "28.9", "k": 1.21, "system": "EJBN30-50 (diamine crosslinker)"},
      {"x": "37.7", "k": 1.85, "system": "EJBN30-60"},
      {"x": "43.4", "k": 2.37, "system": "EJBN30-70"}
    ]
  },
  "10.3390/molecules21050670": {
    "source": "Figure 3 (molecules-21-00670-g003.jpg via PMC CDN, browser-fetched)",
    "method": "visual digitization, max 3 sig figs",
    "note": "GPTMS-surface-treated series digitized (the optimal 3.6 wt%/2.4 wt% treatment used throughout paper); naked (untreated) series digitized separately below but not used for new rows",
    "points": [
      {"x": "10", "k": 0.57, "system": "10.6um treated"},
      {"x": "20", "k": 0.98, "system": "10.6um treated"},
      {"x": "30", "k": 1.95, "system": "10.6um treated"},
      {"x": "40", "k": 2.97, "system": "10.6um treated"},
      {"x": "50", "k": 6.77, "system": "10.6um treated"},
      {"x": "60", "k": 7.44, "system": "10.6um treated"},
      {"x": "70", "k": 6.69, "system": "10.6um treated"},
      {"x": "80", "k": 6.61, "system": "10.6um treated"},
      {"x": "10", "k": 0.56, "system": "3.6um treated"},
      {"x": "20", "k": 0.97, "system": "3.6um treated"},
      {"x": "30", "k": 1.81, "system": "3.6um treated"},
      {"x": "40", "k": 2.58, "system": "3.6um treated"},
      {"x": "50", "k": 2.77, "system": "3.6um treated"},
      {"x": "60", "k": 2.70, "system": "3.6um treated"},
      {"x": "70", "k": 2.12, "system": "3.6um treated"},
      {"x": "80", "k": 1.77, "system": "3.6um treated"}
    ],
    "naked_untreated": [
      {"x": "10", "k": 0.44, "system": "10.6um naked"},
      {"x": "20", "k": 0.77, "system": "10.6um naked"},
      {"x": "30", "k": 1.45, "system": "10.6um naked"},
      {"x": "40", "k": 2.59, "system": "10.6um naked"},
      {"x": "50", "k": 5.76, "system": "10.6um naked"},
      {"x": "60", "k": 6.92, "system": "10.6um naked"},
      {"x": "70", "k": 6.21, "system": "10.6um naked"},
      {"x": "80", "k": 5.39, "system": "10.6um naked"},
      {"x": "10", "k": 0.44, "system": "3.6um naked"},
      {"x": "20", "k": 0.77, "system": "3.6um naked"},
      {"x": "30", "k": 1.45, "system": "3.6um naked"},
      {"x": "40", "k": 2.35, "system": "3.6um naked"},
      {"x": "50", "k": 2.29, "system": "3.6um naked"},
      {"x": "60", "k": 2.25, "system": "3.6um naked"},
      {"x": "70", "k": 1.61, "system": "3.6um naked"},
      {"x": "80", "k": 1.42, "system": "3.6um naked"}
    ]
  }
}

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phase4_figures_digitized.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(DATA, f, indent=2, ensure_ascii=False)
print("wrote", out)
print("polym11071156 points:", len(DATA["10.3390/polym11071156"]["points"]))
print("molecules21050670 treated points:", len(DATA["10.3390/molecules21050670"]["points"]))
