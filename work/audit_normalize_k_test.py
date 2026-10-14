# NEW FILE (audit-only). Independent tests of normalize_k() from work/io_append.py.
# Does not modify production code. Run: python work/audit_normalize_k_test.py
import sys, os, importlib.util

spec = importlib.util.spec_from_file_location(
    "io_append", os.path.join(os.path.dirname(os.path.abspath(__file__)), "io_append.py"))
io = importlib.util.module_from_spec(spec)
spec.loader.exec_module(io)

cases = [
    # (value, unit, expected, label)
    (1.5, "W/mK", 1.5, "basic W/mK"),
    (1.5, "W/(m·K)", 1.5, "unicode middle dot"),
    (1.5, "W m−1 K−1", 1.5, "unicode minus superscript"),
    (1.5, "W m-1 K-1", 1.5, "ascii minus superscript"),
    (1.5, "W·m−1·K−1", 1.5, "dots + unicode minus"),
    (1.5, "Wm−1K−1", 1.5, "no spaces"),
    (1.5, "W (m−1 K−1)", 1.5, "paren form"),
    (1.5, "W/m K", 1.5, "space form"),
    (2500.0, "mW/mK", 2.5, "milliwatt"),
    (2500.0, "mW/m·K", 2.5, "milliwatt dot"),
    (0.25, "W/cmK", 25.0, "per cm"),
    (0.25, "W/cm·K", 25.0, "per cm dot"),
    (0.0015, "W/mmK", 1.5, "per mm"),
    # edge cases / potential traps
    (1.5, "W/mK", 1.5, "lowercase"),
    (1.5, "W/mk", 1.5, "lowercase k"),
    (100.0, "mW/(m·K)", 0.1, "mW paren unicode"),
    (1.0, "W m−1k−1", 1.0, "lowercase k superscript"),
    (1.0, "kW/mK", 1000.0, "kW - NOT in table; fallback path"),
    (1.0, "W/m°C", None, "degC unit - unsupported"),
    (1.0, "cal/(cm·s·K)", None, "cgs unit - unsupported"),
    (1.0, "", None, "empty unit"),
    (1.0, "W", None, "missing k"),
    (1.5, "μW/(m·K)", None, "micro - unsupported (should not silently become 1.5)"),
    (1.5, "W/(m·K)", 1.5, "duplicate-ish"),
    (1.5, "W⋅m−1⋅K−1", 1.5, "bullet operator dots"),
    (1.5, "W m−1k−1", 1.5, "lowercase k no-space superscript"),
]

fails = []
for value, unit, expected, label in cases:
    got = io.normalize_k(value, unit)
    ok = (got == expected) if expected is not None else (got is None)
    mark = "PASS" if ok else "FAIL"
    print(f"[{mark}] {label!r}: normalize_k({value}, {unit!r}) = {got!r} (expected {expected!r})")
    if not ok:
        fails.append((label, value, unit, got, expected))

# specifically check the dangerous fallback branch: 'mm' with m-1 present
got = io.normalize_k(1.5, "W m−1 mm−1")
print(f"[INFO] W m−1 mm−1 (per milli-meter, unicode minus) -> {got!r} (physical expectation 1500.0; table has no entry)")

print()
print(f"TOTAL: {len(cases)} designed cases, {len(fails)} failed")
for f in fails:
    print("  FAIL:", f)
