"""Discovery and fetch runs that read and write data/acquisition/."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from ..build import load_side_files
from ..io import atomic_write_bytes, atomic_write_text, csv_bytes, load_yaml
from ..paths import Layout
from ..records import doi_slug, load_records
from . import europepmc, openalex
from .keys import openalex_key
from .screen import screen

COLUMNS = ["rank", "doi", "title", "year", "venue", "license", "oa_status", "pmcid", "decision", "reason_code",
           "reason", "queries", "cited_by", "openalex_id", "oa_url", "jats", "jats_licence"]


def acq_dir(lay: Layout) -> Path:
    return lay.data / "acquisition"


def cache_dir(lay: Layout) -> Path:
    return lay.root / "sources"


def search(lay: Layout, max_per_query: int | None = None) -> list[dict[str, Any]]:
    cfg = load_yaml(acq_dir(lay) / "queries.yaml")
    key = openalex_key(lay.root)
    n = max_per_query or int(cfg.get("max_results_per_query", 200))
    merged: dict[str, dict[str, Any]] = {}
    for qi, q in enumerate(cfg["queries"]):
        for pos, w in enumerate(openalex.search(q, key, filters=cfg["filters"], max_results=n,
                                                log_path=acq_dir(lay) / "queries.jsonl")):
            if not w["doi"]:
                continue
            m = merged.setdefault(w["doi"], {**w, "rank": pos + 1, "queries": []})
            m["rank"] = min(m["rank"], pos + 1)
            m["queries"].append(str(qi + 1))
    argus = {r.paper.doi.lower() for r in load_records(lay).records}
    _, excl = load_side_files(lay)
    screened = {str(e["doi"]).lower() for e in excl}
    rows = screen(list(merged.values()), argus, screened)
    for r in rows:
        r["queries"] = ";".join(r["queries"])
        r.setdefault("jats", "")
        r.setdefault("jats_licence", "")
    rows.sort(key=lambda r: (r["decision"] != "include", r["rank"], -int(r.get("cited_by") or 0), r["doi"]))
    write(lay, rows)
    return rows


def read(lay: Layout) -> list[dict[str, Any]]:
    p = acq_dir(lay) / "candidates.csv"
    return list(csv.DictReader(p.open(encoding="utf-8-sig"))) if p.exists() else []


def write(lay: Layout, rows: list[dict[str, Any]]) -> None:
    atomic_write_bytes(acq_dir(lay) / "candidates.csv", csv_bytes(rows, COLUMNS))


def fetch(lay: Layout, limit: int) -> list[dict[str, Any]]:
    """Europe PMC JATS for the first `limit` included candidates that have a PMCID."""
    rows = read(lay)
    done = []
    for r in rows:
        if len(done) >= limit:
            break
        if r["decision"] != "include" or r.get("jats") == "none":
            continue
        if not r["pmcid"]:
            r["pmcid"] = europepmc.lookup_pmcid(r["doi"]) or ""
            if not r["pmcid"]:
                r["jats"] = "none"
                continue
        xml = europepmc.fetch_jats(r["pmcid"], r["doi"], cache_dir(lay) / "jats")
        if xml is None:
            r["jats"] = "none"
            continue
        info = europepmc.render(xml)
        txt = cache_dir(lay) / "text" / f"{doi_slug(r['doi'])}.txt"
        txt.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(txt, info["text"])
        r["jats"] = txt.relative_to(lay.root).as_posix()
        r["jats_licence"] = info["licence"]
        done.append(r)
    write(lay, rows)
    return done
