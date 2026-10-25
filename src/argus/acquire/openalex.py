"""OpenAlex discovery. One call per page; every query is appended to the query log."""
from __future__ import annotations

import datetime as _dt
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from ..external.harmonize import normalize_doi
from .keys import redact

API = "https://api.openalex.org/works"
USER_AGENT = "argus-dataset-tool (course project; https://github.com/KumarSrinidhi/sctproject)"
SELECT = ("id,doi,title,publication_year,type,language,primary_location,best_oa_location,open_access,ids,"
          "abstract_inverted_index,cited_by_count")


def abstract_text(inv: dict[str, list[int]] | None) -> str:
    """OpenAlex stores abstracts as {word: [positions]}; rebuild the text."""
    if not inv:
        return ""
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


def _get(url: str, key: str, retries: int = 3) -> dict[str, Any]:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt * 2)
                continue
            raise RuntimeError(redact(f"OpenAlex HTTP {e.code} for {url}", key)) from None
    raise RuntimeError("unreachable")


def work_record(w: dict[str, Any]) -> dict[str, Any]:
    oa = w.get("best_oa_location") or {}
    prim = w.get("primary_location") or {}
    src = (prim.get("source") or {}) if isinstance(prim, dict) else {}
    ids = w.get("ids") or {}
    pmcid = str(ids.get("pmcid") or "").rstrip("/").rsplit("/", 1)[-1]
    return {
        "doi": normalize_doi(w.get("doi")),
        "title": " ".join(str(w.get("title") or "").split()),
        "year": w.get("publication_year"),
        "type": w.get("type") or "",
        "venue": src.get("display_name") or "",
        "oa_status": (w.get("open_access") or {}).get("oa_status") or "",
        "license": oa.get("license") or "",
        "oa_url": oa.get("pdf_url") or oa.get("landing_page_url") or "",
        "pmcid": pmcid if pmcid.upper().startswith("PMC") else "",
        "openalex_id": str(w.get("id") or "").rsplit("/", 1)[-1],
        "cited_by": w.get("cited_by_count") or 0,
        "abstract": abstract_text(w.get("abstract_inverted_index")),
    }


def search(query: str, key: str, *, filters: str, max_results: int, log_path: Path | None = None) -> list[dict[str, Any]]:
    """Relevance-ranked works for a full-text query; up to max_results (200 per page)."""
    out: list[dict[str, Any]] = []
    cursor = "*"
    calls = 0
    count = None
    while cursor and len(out) < max_results:
        params = {"search": query, "filter": filters, "per_page": str(min(200, max_results - len(out))),
                  "cursor": cursor, "select": SELECT, "api_key": key}
        d = _get(API + "?" + urllib.parse.urlencode(params), key)
        calls += 1
        count = d["meta"]["count"]
        out += [work_record(w) for w in d["results"]]
        cursor = d["meta"].get("next_cursor") if d["results"] else None
        time.sleep(0.2)
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {"time": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"), "service": "openalex",
                 "query": query, "filter": filters, "total_matches": count, "returned": len(out), "calls": calls}
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return out
