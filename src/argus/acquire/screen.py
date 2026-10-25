"""Title/abstract screening with explicit, reproducible rules.

Each candidate gets one decision and a reason code; the rules are deliberately
simple so that a reader can audit them. Inclusion only means "worth fetching
the full text": values still have to be found and checked in the paper itself.
"""
from __future__ import annotations

import re
from typing import Any

K_RX = re.compile(r"thermal(?:ly)?\s+conduct", re.I)
FILLER_RX = re.compile(r"boron\s+nitride|\bh-?BN\b|\bBNNS\b|\bBN\b|\bc-?BN\b|alumin(?:i)?um\s+nitride|\bAlN\b", re.I)
POLYMER_RX = re.compile(r"epox|polymer|resin|silicone|\bPDMS\b|polyimide|\bPI\b|\bPVDF\b|polyvinyl|\bPVA\b|"
                        r"polyethylene|\bPE\b|polypropylene|\bPP\b|polyurethane|\bPU\b|polystyrene|polyamide|"
                        r"elastomer|rubber|thermoset|thermoplastic|nanocomposite|composite", re.I)
REVIEW_RX = re.compile(r"\breview\b|state of the art|progress in|perspective|overview", re.I)
SIM_RX = re.compile(r"molecular\s+dynamics|first[- ]principles|\bDFT\b|finite[- ]element|simulation|machine\s+learning|"
                    r"numerical|model(?:l)?ing\s+of", re.I)
EXPERIMENT_RX = re.compile(r"prepar|fabricat|synthes|measur|laser\s+flash|hot\s+disk|experiment|filled|loading|wt\s*%|vol\s*%",
                           re.I)
NON_POLYMER_RX = re.compile(r"sintered|ceramic\s+matrix|\bglass\s+matrix|metal\s+matrix|nanofluid", re.I)
OPEN_LICENCES = ("cc-by", "cc0", "public-domain")

REASONS = {
    "include": "worth fetching: thermal conductivity of a BN/AlN-filled polymer, experimental",
    "already-in-argus": "paper already has an ARGUS record",
    "already-screened": "already listed in data/exclusions.yaml",
    "no-doi": "no DOI",
    "not-article": "not a journal article",
    "review": "review or perspective",
    "no-k": "title and abstract do not mention thermal conductivity",
    "no-target-filler": "no BN or AlN filler in title or abstract",
    "no-polymer": "no polymer matrix in title or abstract",
    "non-polymer-matrix": "ceramic, glass or metal matrix, or a nanofluid",
    "simulation-only": "modelling or simulation without experimental wording",
    "not-open": "no open licence recorded by OpenAlex",
}


def decide(c: dict[str, Any], argus_dois: set[str], screened_dois: set[str]) -> str:
    title, abstract = c.get("title", ""), c.get("abstract", "")
    text = f"{title} {abstract}"
    if not c.get("doi"):
        return "no-doi"
    if c["doi"] in argus_dois:
        return "already-in-argus"
    if c["doi"] in screened_dois:
        return "already-screened"
    if c.get("type") not in ("article", ""):
        return "review" if c.get("type") == "review" else "not-article"
    if REVIEW_RX.search(title):
        return "review"
    if not K_RX.search(text):
        return "no-k"
    if not FILLER_RX.search(text):
        return "no-target-filler"
    if not POLYMER_RX.search(text):
        return "no-polymer"
    if NON_POLYMER_RX.search(title):
        return "non-polymer-matrix"
    if SIM_RX.search(title) and not EXPERIMENT_RX.search(abstract):
        return "simulation-only"
    if not str(c.get("license", "")).lower().startswith(OPEN_LICENCES):
        return "not-open"
    return "include"


def screen(candidates: list[dict[str, Any]], argus_dois: set[str], screened_dois: set[str]) -> list[dict[str, Any]]:
    out = []
    for c in candidates:
        d = decide(c, argus_dois, screened_dois)
        out.append({**c, "decision": "include" if d == "include" else "exclude", "reason_code": d,
                    "reason": REASONS[d]})
    return out
