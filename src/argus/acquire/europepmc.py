"""Europe PMC full text (JATS XML) for open-access papers with a PMCID.

The XML is cached under sources/ (git-ignored) with its licence. A plain-text
rendering keeps tables as rows of cells separated by " | ", so that an
extractor can quote table rows verbatim and the quote checker can find them.
"""
from __future__ import annotations

import re
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from ..io import atomic_write_bytes
from ..records import doi_slug

REST = "https://www.ebi.ac.uk/europepmc/webservices/rest/{pmcid}/fullTextXML"
USER_AGENT = "argus-dataset-tool (course project; https://github.com/KumarSrinidhi/sctproject)"
XLINK = "{http://www.w3.org/1999/xlink}href"


SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def lookup_pmcid(doi: str, timeout: float = 30.0) -> str:
    """PMCID of an open-access paper whose full text Europe PMC holds, else ''."""
    import json
    import urllib.parse

    url = SEARCH + "?" + urllib.parse.urlencode({"query": f'DOI:"{doi}"', "format": "json", "resultType": "lite"})
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        res = json.load(r)["resultList"]["result"]
    time.sleep(0.2)
    for x in res:
        if str(x.get("doi", "")).lower() == doi.lower() and x.get("pmcid") and x.get("inEPMC") == "Y" \
                and x.get("isOpenAccess") == "Y":
            return x["pmcid"]
    return ""


def fetch_jats(pmcid: str, doi: str, cache: Path, timeout: float = 60.0) -> Path | None:
    """Download (once) and cache the JATS XML; None when Europe PMC has no full text."""
    path = cache / f"{doi_slug(doi)}.xml"
    if path.exists() and path.stat().st_size > 0:
        return path
    req = urllib.request.Request(REST.format(pmcid=pmcid), headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    time.sleep(0.3)
    if not data.strip().startswith(b"<"):
        return None
    cache.mkdir(parents=True, exist_ok=True)
    atomic_write_bytes(path, data)
    return path


def _text(el: ET.Element | None) -> str:
    return " ".join("".join(el.itertext()).split()) if el is not None else ""


def licence(root: ET.Element) -> str:
    lic = root.find(".//permissions/license")
    if lic is None:
        return ""
    href = lic.get(XLINK) or ""
    if not href:
        ref = lic.find(".//{http://www.niso.org/schemas/ali/1.0/}license_ref")
        href = (ref.text or "") if ref is not None else ""
    return href or _text(lic)[:120]


def render(xml_path: Path) -> dict[str, Any]:
    """Title, licence and a plain-text rendering (sections, captions, tables as ' | ' rows)."""
    root = ET.parse(xml_path).getroot()
    out: list[str] = []
    title = _text(root.find(".//article-meta/title-group/article-title"))
    out += [f"TITLE: {title}", ""]
    abstract = root.find(".//article-meta/abstract")
    if abstract is not None:
        out += ["ABSTRACT", _text(abstract), ""]
    body = root.find(".//body")

    def walk(el: ET.Element, depth: int = 0) -> None:
        for ch in el:
            tag = ch.tag
            if tag == "sec":
                head = _text(ch.find("title"))
                if head:
                    out.append("#" * min(depth + 1, 4) + " " + head)
                walk(ch, depth + 1)
            elif tag == "p":
                out.append(_text(ch))
                out.append("")
            elif tag in ("table-wrap", "fig"):
                label = _text(ch.find("label"))
                cap = _text(ch.find("caption"))
                out.append(f"[{label}] {cap}".strip())
                for tr in ch.iter("tr"):
                    cells = [_text(c) for c in tr if c.tag in ("td", "th")]
                    if any(cells):
                        out.append(" | ".join(cells))
                foot = _text(ch.find("table-wrap-foot"))
                if foot:
                    out.append(f"(table footnote) {foot}")
                out.append("")
            elif tag not in ("title", "label"):
                walk(ch, depth)

    if body is not None:
        walk(body)
    # tables and figures placed in floats-group (common in PMC)
    floats = root.find(".//floats-group")
    if floats is not None:
        walk(floats)
    text = "\n".join(out)
    return {"title": title, "licence": licence(root), "text": re.sub(r"\n{3,}", "\n\n", text)}
