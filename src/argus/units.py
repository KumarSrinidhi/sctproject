"""Unit handling for thermal conductivity and filler loading.

Fixes audit finding D4: the legacy `normalize_k()` was never called, left
kW/(m K) unscaled and accepted anything containing 'w', 'm' and 'k'. Here an
unrecognised unit returns None so the validator can block the row.
"""
from __future__ import annotations

import re
import unicodedata

# Power prefix on the watt.
_POWER = {"": 1.0, "m": 1e-3, "k": 1e3, "u": 1e-6, "μ": 1e-6, "µ": 1e-6}
# Length unit in the denominator. A per-kelvin and per-degree-Celsius
# conductivity are identical (it is a temperature *difference*).
_LENGTH = {"m": 1.0, "cm": 1e-2, "mm": 1e-3}
_TEMP = r"(?:k|°c|c)"

# Non-SI units sometimes seen in older literature (canonical form -> factor).
_HR = r"(?:h|hr)"
_OTHER_UNITS = {
    # cal/(cm s K), any order of cm and s
    rf"^cal(?:/(?:cm|s){{2}}-?{_TEMP}|cm-1s-1{_TEMP}-1|s-1cm-1{_TEMP}-1)$": 418.4,
    # BTU/(h ft F)
    rf"^btu/(?:{_HR}-?ft|ft-?{_HR})-?°?f$": 1.730735,
    # BTU in/(h ft^2 F)
    rf"^btu-?in/{_HR}-?ft2-?°?f$": 0.1442279,
}

_DASHES = dict.fromkeys(map(ord, "−–—‐‑"), "-")
_DROP = re.compile(r"[\s·∙⋅•*.\[\]{}()]")


def canonical_unit(unit: str) -> str:
    """Lower-case, ASCII-ish, separator-free form of a unit string."""
    u = unicodedata.normalize("NFKC", unit or "").strip().lower()
    u = u.split("(=")[0]  # drop trailing restatements like "W/K.m (= W/(m K))"
    u = u.translate(_DASHES).replace("^", "").replace("⁻¹", "-1").replace("º", "°")
    u = u.replace("per", "/")
    return _DROP.sub("", u)


def _si_patterns() -> list[re.Pattern[str]]:
    L = "(?P<len>cm|mm|m)"
    T = _TEMP
    forms = [
        rf"/{L}-?{T}",  # W/mK, W/m-K, W/(m K)
        rf"/{T}-?{L}",  # W/K.m
        rf"{L}-1{T}-1",  # W m-1 K-1
        rf"{T}-1{L}-1",  # W K-1 m-1
    ]
    return [re.compile(rf"^(?P<pow>[mkuμµ]?)w{f}$") for f in forms]


_SI = _si_patterns()


def k_unit_factor(unit: str) -> float | None:
    """Multiplier converting a value in `unit` to W/(m K), or None if unknown."""
    u = canonical_unit(unit)
    if not u:
        return None
    for pat in _SI:
        m = pat.match(u)
        if m:
            return _POWER[m.group("pow")] / _LENGTH[m.group("len")]
    for pat, factor in _OTHER_UNITS.items():
        if re.match(pat, u):
            return factor
    return None


def normalize_k(value: float, unit: str) -> float | None:
    """Convert a conductivity to W/(m K). Returns None for unknown units."""
    f = k_unit_factor(unit)
    if f is None:
        return None
    return round(float(value) * f, 9)


# --------------------------------------------------------------------------- loading

def wt_to_vol(wt_pct: float, rho_filler: float, rho_matrix: float) -> float:
    """Weight percent -> volume percent for a two-phase, void-free composite."""
    w = wt_pct / 100.0
    if not 0.0 <= w <= 1.0:
        raise ValueError(f"wt% out of range: {wt_pct}")
    if w == 0.0:
        return 0.0
    vf = w / rho_filler
    vm = (1.0 - w) / rho_matrix
    return 100.0 * vf / (vf + vm)


def vol_to_wt(vol_pct: float, rho_filler: float, rho_matrix: float) -> float:
    """Volume percent -> weight percent for a two-phase, void-free composite."""
    v = vol_pct / 100.0
    if not 0.0 <= v <= 1.0:
        raise ValueError(f"vol% out of range: {vol_pct}")
    mf = v * rho_filler
    mm = (1.0 - v) * rho_matrix
    return 100.0 * mf / (mf + mm) if (mf + mm) else 0.0


def phr_to_wt(phr: float) -> float:
    """Parts per hundred resin -> weight percent of filler in the composite."""
    return 100.0 * phr / (100.0 + phr)
