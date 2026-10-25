"""Every extracted value carries a verbatim quote; this checks the quote is in the source."""
from __future__ import annotations

import re
import unicodedata

_DASH = dict.fromkeys(map(ord, "‐‑‒–—−"), "-")


def norm(s: str) -> str:
    """Compare quotes and sources after harmless normalisation: Unicode NFKC, dashes,
    whitespace, case, and the spacing around table separators."""
    s = unicodedata.normalize("NFKC", s or "").translate(_DASH)
    s = s.replace("·", " ").replace("×", "x")
    s = re.sub(r"\s*\|\s*", " | ", s)
    return re.sub(r"\s+", " ", s).strip().lower()


def quote_in_source(quote: str, source_text: str) -> bool:
    q = norm(quote)
    return bool(q) and q in norm(source_text)


_APPROX = re.compile(r"(?:~|≈|∼|\babout|\bapprox(?:\.|imately)?|\bnearly|\baround|\bover|\bmore than|\babove|"
                     r"\bup to|\bexceed(?:s|ing)?|>|<)\s*$", re.I)


def approximate_k(value: float, quote: str) -> bool:
    """True if the printed k is given as approximate or as a bound ('~15', 'over 9', 'up to 3.1')."""
    q = (quote or "").replace(",", ".")
    for m in re.finditer(r"\d+(?:\.\d+)?", q):
        if abs(float(m.group()) - float(value)) < 1e-9 and _APPROX.search(q[max(0, m.start() - 14):m.start()]):
            return True
    return False


def number_in_quote(value: float, quote: str) -> bool:
    """The reported number must appear in its quote (as printed, e.g. 1.2 or 1.20)."""
    nums = re.findall(r"\d+(?:\.\d+)?", (quote or "").replace(",", "."))
    return any(abs(float(n) - float(value)) < 1e-9 for n in nums)
