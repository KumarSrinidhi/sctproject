"""Controlled vocabularies: map free-text fields to analysis-ready classes.

The raw record text is never changed. These functions only *derive* labels,
and every derived label carries a basis so a reader can tell a reported fact
from an inference (see enrich.py).

Method taxonomy and direction semantics follow the 2026-10-22 research pass
(docs/reports/BN epoxy thermal conductivity research.md, measurement section):
isotropic-mode transient plane source, transient hot bridge and hot wire sense
a mix of in-plane and through-plane conduction (about the geometric mean) in an
anisotropic sample, while laser flash on a standard disc holder and steady-state
heat-flow rigs sense the through-plane value.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Any

import yaml


# --------------------------------------------------------------------------- methods

@dataclass(frozen=True)
class MethodClass:
    id: str
    family: str  # transient | steady-state | periodic | optical | unspecified
    quantity: str  # what the instrument fundamentally measures
    direction: str  # what it senses in a plate-like anisotropic sample
    rel_uncertainty: float  # judgement-based 1-sigma default when the paper gives none
    description: str


METHOD_CLASSES: dict[str, MethodClass] = {m.id: m for m in [
    MethodClass("LFA", "transient", "diffusivity", "through-plane", 0.08,
                "Laser / xenon flash (ASTM E1461, ISO 22007-4); k = alpha * rho * Cp. Standard holder senses through-plane."),
    MethodClass("TPS", "transient", "conductivity+diffusivity", "mixed", 0.05,
                "Transient plane source / Hot Disk (ISO 22007-2). Isotropic mode reports ~sqrt(k_in * k_through)."),
    MethodClass("THB", "transient", "conductivity+diffusivity", "mixed", 0.05,
                "Transient hot bridge (Linseis THB); planar sensor, assumed to behave like isotropic TPS."),
    MethodClass("MTPS", "transient", "effusivity", "mixed", 0.06,
                "Modified transient plane source (C-Therm TCi/Trident); effusivity-primary, direction weighting undocumented."),
    MethodClass("HOT_WIRE", "transient", "conductivity", "mixed", 0.06,
                "Transient hot wire / needle probe / quick thermal conductivity meter (line source)."),
    MethodClass("SS_D5470", "steady-state", "thermal resistance", "through-plane", 0.10,
                "Steady-state heat flow under pressure (ASTM D5470, DRL-type). Single-thickness values include contact resistance."),
    MethodClass("SS_GHFM", "steady-state", "thermal resistance", "through-plane", 0.07,
                "Guarded heat flow meter (ASTM E1530, e.g. DTC-300)."),
    MethodClass("SS_HFM_GHP", "steady-state", "conductivity", "through-plane", 0.05,
                "Heat flow meter / guarded hot plate (ASTM C518, C177, ISO 8302)."),
    MethodClass("SS_UNSPECIFIED", "steady-state", "conductivity", "through-plane", 0.10,
                "Steady-state method named without the apparatus."),
    MethodClass("PERIODIC", "periodic", "diffusivity", "as-reported", 0.08,
                "Periodic heating / temperature-wave / laser-spot Angstrom methods (ISO 22007-3, ULVAC Laser-PIT, Bethel TA)."),
    MethodClass("THIN_FILM", "optical", "conductivity", "through-plane", 0.10,
                "3-omega, TDTR, FDTR (thin films; local cross-plane)."),
    MethodClass("IR_THERMO", "optical", "conductivity", "as-reported", 0.10,
                "IR thermography / lock-in thermography / hot-plate + IR camera comparative setups."),
    MethodClass("UNSPECIFIED", "unspecified", "unknown", "unknown", 0.10,
                "Method not stated in the available text."),
]}

# Tier 1: a technique is named. When several are named ("Hot disk (this work);
# laser flash for literature rows", "LFA ...; IR camera validation"), the one
# mentioned FIRST is the method used for the value.
_NAMED: list[tuple[str, str]] = [
    ("LFA", r"laser\s*flash|light\s*flash|xenon\s*flash|\bLFA\b|LFA[\s-]?\d|LAF\s?\d|nano\s?flash|hyper\s?flash|"
            r"micro\s?flash|sinku|DXF-?\d|e1461|22007-4"),
    ("PERIODIC", r"laser[\s-]?pit|periodic\s*heating|temperature[\s-]wave|thermowave|ångström|angstrom|22007-3"),
    ("TPS", r"hot\s*disk|transient\s*plane|TPS\s?\d|22007-2|DZDR|DRE-?\d|transient\s*plate"),
    ("THB", r"hot\s*bridge|\bTHB\b"),
    ("MTPS", r"c-therm|\bTCi\b|trident|modified\s*transient"),
    ("HOT_WIRE", r"hot[\s-]*wire|needle\s*probe|line\s*source|xiaxi|xiatech"),
    ("SS_D5470", r"d5470|DRL-?I|plane\s*heat\s*flow"),
    ("SS_GHFM", r"e1530|DTC-?\d|guarded\s*heat\s*flow|unitherm"),
    ("SS_HFM_GHP", r"c518|c177|guarded\s*hot\s*plate|HFM\s?\d|8302"),
    ("THIN_FILM", r"3\s?ω|3[\s-]?omega|thermoreflectance|TDTR|FDTR"),
    ("IR_THERMO", r"thermo[\s-]?camera|ir\s*camera|infrared\s*therm|lock-?in\s*therm"),
]
# Tier 1b: bare abbreviations ("TPS, 2500S", "THW, ASTM C1113", "GHP", "HFM"). They count
# only when no tier-1 name, standard or instrument is present, so "GHP, DRL-III" stays
# a D5470-type rig.
_ABBREV: list[tuple[str, str]] = [
    ("TPS", r"\bTPS\b"),
    ("HOT_WIRE", r"\bTHW\b"),
    ("SS_HFM_GHP", r"\bGHP\b|\bHFM\b"),
]
# Tier 2: only the family is named.
_GENERIC: list[tuple[str, str]] = [("SS_UNSPECIFIED", r"steady[\s-]*state")]
# Tier 3: only an instrument model is named. "TC-3000" is both a Sinku-Riko
# laser flash (caught in tier 1 by "laser flash"/"Sinku") and a Xi'an Xiaxi hot
# wire; Xiangyi's "quick thermal conductivity meter" is a TPS-type clone while
# KEM's QTM is a hot-wire probe.
_INSTRUMENT: list[tuple[str, str]] = [
    ("TPS", r"quick\s*thermal\s*conductivity\s*meter.*xiangyi|xiangyi.*quick"),
    ("HOT_WIRE", r"quick\s*thermal\s*conductivity\s*meter|\bQTM\b|\bKEM\b"),
    ("HOT_WIRE", r"\bTC[\s-]?3000\b"),
]


def _compile(rules: list[tuple[str, str]]) -> list[tuple[str, re.Pattern[str]]]:
    return [(cls, re.compile(rx, re.IGNORECASE)) for cls, rx in rules]


_NAMED_RX, _ABBREV_RX = _compile(_NAMED), _compile(_ABBREV)
_GENERIC_RX, _INSTRUMENT_RX = _compile(_GENERIC), _compile(_INSTRUMENT)


@dataclass(frozen=True)
class MethodLabel:
    method_class: str
    basis: str  # named | generic | instrument | none
    info: MethodClass


def classify_method(text: str | None) -> MethodLabel:
    t = text or ""
    for tier in (_NAMED_RX, _ABBREV_RX):
        hits = [(m.start(), cls) for cls, rx in tier if (m := rx.search(t))]
        if hits:
            cls = min(hits)[1]
            return MethodLabel(cls, "named", METHOD_CLASSES[cls])
    for tier, basis in ((_GENERIC_RX, "generic"), (_INSTRUMENT_RX, "instrument")):
        for cls, rx in tier:
            if rx.search(t):
                return MethodLabel(cls, basis, METHOD_CLASSES[cls])
    return MethodLabel("UNSPECIFIED", "none", METHOD_CLASSES["UNSPECIFIED"])


_DSC_RHO = re.compile(r"\bDSC\b|densimeter|archimedes|water\s*displacement|density\s*by|measured\s*density|"
                      r"cp\s*(?:by|from|via)?\s*dsc", re.IGNORECASE)


def lfa_cp_rho_reported(text: str | None) -> bool:
    """True if the method text says how Cp or density was obtained (DSC, Archimedes ...)."""
    return bool(_DSC_RHO.search(text or ""))


# --------------------------------------------------------------------------- direction

DIRECTIONS = ("in-plane", "through-plane", "isotropic", "mixed", "unknown")

_DIR_RULES = [
    ("in-plane", re.compile(r"in[\s-]?plane|sheet\s*plane|parallel\s*to\s*(?:the\s*)?(?:film|sheet|surface)", re.I)),
    ("through-plane", re.compile(r"through[\s-]?(?:plane|thickness)|out[\s-]?of[\s-]?plane|cross[\s-]?plane|"
                                 r"vertical|perpendicular|normal\s*to", re.I)),
    ("isotropic", re.compile(r"isotropic", re.I)),
]


def normalize_direction(text: str | None) -> str:
    """Map a reported k_direction string onto in-plane | through-plane | isotropic | unknown."""
    t = (text or "").strip()
    if not t or t.lower() == "unknown":
        return "unknown"
    for label, rx in _DIR_RULES:
        if rx.search(t):
            return label
    return "unknown"


def direction_hint(text: str | None) -> str:
    """A single unambiguous direction mentioned in free text (e.g. a method
    description 'LFA ... perpendicular to film plane'), else 'unknown'.
    Text naming both directions ('in-plane and cross-plane') gives 'unknown'."""
    t = text or ""
    found = {label for label, rx in _DIR_RULES[:2] if rx.search(t)}
    return found.pop() if len(found) == 1 else "unknown"


# --------------------------------------------------------------------------- fillers

FILLER_BASES = ("h-BN", "BN", "BNNS", "cBN", "AlN", "Al2O3", "MgO")
BN_FAMILY = frozenset({"h-BN", "BN", "BNNS", "cBN"})
PLATELET_BN = frozenset({"h-BN", "BN", "BNNS"})


@dataclass(frozen=True)
class FillerLabel:
    family: str  # BN | AlN | Al2O3 | MgO | hybrid | none | other
    base: str  # single-filler base label ('' for hybrids/none)
    components: tuple[str, ...]
    is_hybrid: bool
    contains_bn: bool


def classify_filler(label: str | None) -> FillerLabel:
    s = (label or "").strip()
    if not s or s.lower() == "none":
        return FillerLabel("none", "", (), False, False)
    is_hybrid = "hybrid" in s.lower() or bool(re.search(r"[/+]", s))
    core = re.sub(r"\bhybrid\b", "", s, flags=re.I).strip()
    comps = tuple(c.strip() for c in re.split(r"[/+]", core) if c.strip())
    contains_bn = any(c in BN_FAMILY or c.upper().endswith("BN") or "BNNS" in c for c in comps)
    if is_hybrid:
        return FillerLabel("hybrid", "", comps, True, contains_bn)
    base = comps[0] if comps else s
    if base in BN_FAMILY:
        fam = "BN"
    elif base in ("AlN", "Al2O3", "MgO"):
        fam = base
    else:
        fam = "other"
    return FillerLabel(fam, base, comps, False, contains_bn)


# --------------------------------------------------------------------------- matrices

_MATRIX_RULES = [
    ("silicone", re.compile(r"silicone|pdms|polydimethylsiloxane|siloxane|\bSiR\b|\bSG\b", re.I)),
    ("polyimide", re.compile(r"polyimide|\bPI\b", re.I)),
    ("PEG", re.compile(r"\bPEG\b|polyethylene\s*glycol", re.I)),
    ("polystyrene", re.compile(r"polystyrene|\bPS\b", re.I)),
    ("polyurethane", re.compile(r"polyurethane|\bPU\b", re.I)),
    ("epoxy", re.compile(r"epox|dgeba|\bEP\b|\bEMC\b|araldite|novolac|\bE-?51\b|\bE-?828\b|\bYD-?128\b|\bCEP\b|"
                         r"\bRIP\b|cyanate", re.I)),
    # Thermoplastics added with Phase 6 (they come after every rule above, so no earlier row changes family).
    ("polyethylene", re.compile(r"\b(?:HD|LD|LLD|UHMW)?PE\b(?!-g)|polyethylene(?!\s*(?:glycol|terephthalate|oxide|imine))",
                                re.I)),
    ("polypropylene", re.compile(r"polypropylene|\bPP\b", re.I)),
    ("polyamide", re.compile(r"polyamide|nylon|polyphthalamide|\bPA\s?6{1,2}\b|\bPPA\b", re.I)),
    ("PVDF", re.compile(r"\bPVDF\b|poly\s*\(?\s*vinylidene\s*fluoride", re.I)),
    ("PVA", re.compile(r"\bc?PVA\b|poly\s*\(?\s*vinyl\s*alcohol", re.I)),
    ("PPS", re.compile(r"\bPPS\b|poly\s*\(?\s*phenylene\s*sulfide", re.I)),
    ("PEI", re.compile(r"polyetherimide|\bPEI\b", re.I)),
    ("polycarbonate", re.compile(r"polycarbonate|\bPC\b", re.I)),
    ("PMMA", re.compile(r"\bPMMA\b|poly\s*\(?\s*methyl\s*methacrylate", re.I)),
]
_PREFILLED = re.compile(r"containing\s+\S+\s+(?:and\s+\S+\s+)?fillers|already\s+loaded", re.I)


def classify_matrix(text: str | None) -> str:
    t = text or ""
    for fam, rx in _MATRIX_RULES:
        if rx.search(t):
            return fam
    return "other"


def matrix_prefilled(text: str | None) -> bool:
    """Commercial resins sold with filler already in them: wt% cannot be converted."""
    return bool(_PREFILLED.search(text or ""))


# --------------------------------------------------------------------------- reference data

@lru_cache(maxsize=1)
def reference() -> dict[str, Any]:
    with resources.files("argus").joinpath("reference/materials.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def filler_props(base: str) -> dict[str, Any] | None:
    ref = reference()["fillers"]
    p = ref.get(base)
    if p and "alias_of" in p:
        p = ref[p["alias_of"]]
    return p


def matrix_props(family: str) -> dict[str, Any] | None:
    return reference()["matrices"].get(family)
