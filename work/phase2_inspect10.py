import json, hashlib, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
inp = json.load(open("work/audit_phase2_inputs.json", encoding="utf-8"))
t = Path(r"C:\Users\IVERME~1\AppData\Local\Temp\opencode\phase2_restore_test2")
ok = True
for name, h in inp["baseline_hashes"].items():
    p = (t / "work" / name) if name.endswith(".jsonl") else (t / name)
    got = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    if got != h: ok = False; print("MISMATCH", name, got, h)
print("sandbox restore byte-identical to Phase 1 baseline:", ok)
# live files still Phase-2 state?
live = hashlib.sha256(Path("thermal_conductivity_dataset.csv").read_bytes()).hexdigest()[:16]
print("live dataset hash (Phase 2 state expected):", live, "| baseline was", inp["baseline_hashes"]["thermal_conductivity_dataset.csv"])
