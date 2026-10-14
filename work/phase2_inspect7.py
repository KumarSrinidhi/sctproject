import sys, glob
sys.stdout.reconfigure(encoding="utf-8")
pairs = [
 ("10.1039/c8ra10211b",
  "3D BN/PA66 aerogel scaffolds for epoxy composites with enhanced thermal conductivity",
  "Improved dielectric stability of epoxy composites with ultralow boron nitride loading"),
 ("10.3390/polym11121990",
  "Magnetically aligned nickel powder in AlN/epoxy composites with enhanced thermal conductivity",
  "Effect of Particle Sizes of Nickel Powder on Thermal Conductivity of Epoxy Resin-Based Composites under Magnetic Alignment"),
 ("10.3390/nano8120997",
  "Synergistic Effects of Functionalized CNTs and h-BN on Enhanced Thermal Conductivity of Epoxy/Cyanate Ester Composites",
  "Synergistic Effects of Functional CNTs and h-BN on Enhanced Thermal Conductivity of Epoxy/Cyanate Matrix Composites"),
]
import os
for doi, old, new in pairs:
    fn = "work/fulltext/" + doi.replace("/", "_").replace(".", "_")[:3]  # no-op
    cands = [p for p in glob.glob("work/fulltext/*.txt") if doi.split("/")[1][:8] in p and doi.split("/")[0][-3:] in p]
    if not cands:
        cands = [p for p in glob.glob("work/fulltext/*.txt") if doi.replace("/","_").replace(".","_")[:14] in p.replace(".","_")]
    print(doi, "->", cands)
    for p in cands:
        t = open(p, encoding="utf-8", errors="replace").read()
        print("   corrected present:", new.lower() in t.lower(), "| old present:", old.lower() in t.lower())
