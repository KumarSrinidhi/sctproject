import sys
sys.stdout.reconfigure(encoding="utf-8")
readme = open("README.md", encoding="utf-8").read()
for a in [
 "| `paper_inventory.csv` | 63 papers with row counts, fillers, matrices, k ranges |",
 "**Primary (epoxy + BN/AlN):** 158 epoxy-based rows; h-BN (61) + BN (45) + BNNS (43) + AlN (22) = 171 BN/AlN-family rows.",
 "**Optional matrices (tagged in notes):** silicone rubber (14), polyimide (9), PDMS (2), PEG PCM (2), polystyrene (2), polyurethane (1), liquid crystal epoxy (included in epoxy-based count).",
]:
    print("OK " if a in readme else "MISSING: " + a[:90])
