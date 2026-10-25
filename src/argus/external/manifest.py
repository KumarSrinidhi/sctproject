"""data/external/sources.yaml: what each external dataset is, its licence, and
the sha256 of every raw file, so a changed or corrupted download is caught."""
from __future__ import annotations

import hashlib
import urllib.request
from pathlib import Path
from typing import Any

from ..io import atomic_write_bytes, load_yaml

MANIFEST = "sources.yaml"
USER_AGENT = "argus-dataset-tool (course project; https://github.com/KumarSrinidhi/sctproject)"


def load(folder: Path) -> dict[str, Any]:
    path = folder / MANIFEST
    return (load_yaml(path) or {}).get("sources", {}) if path.exists() else {}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_files(folder: Path) -> list[dict[str, Any]]:
    """One entry per manifest file: present? checksum ok?"""
    out = []
    for key, src in load(folder).items():
        for f in src.get("files", []):
            p = folder / f["path"]
            present = p.exists()
            got = sha256(p) if present else None
            out.append({"source": key, "path": f["path"], "present": present,
                        "committed": f.get("committed", True),
                        "ok": present and got == f["sha256"], "sha256": got})
    return out


def source_state(files: list[dict[str, Any]], source: str) -> str:
    """One word per source, with the same rule as `argus external check`:
    no raw files | ok | not fetched (only on-demand files absent) | CHANGED | MISSING."""
    mine = [f for f in files if f["source"] == source]
    if not mine:
        return "no raw files"
    if any(f["present"] and not f["ok"] for f in mine):
        return "CHANGED"
    if any(not f["present"] and f["committed"] for f in mine):
        return "MISSING"
    if any(not f["present"] for f in mine):
        return "ok (on-demand files not fetched)"
    return "ok"


class UnknownSource(KeyError):
    pass


def fetch(folder: Path, only: str | None = None, timeout: float = 60.0) -> list[dict[str, Any]]:
    """Download missing raw files from their recorded URL and verify the checksum.
    A file whose checksum does not match is not written; a download error is
    reported for that file and the others are still tried."""
    import urllib.error

    srcs = load(folder)
    if only and only not in srcs:
        raise UnknownSource(f"unknown source {only!r}; known: {sorted(srcs)}")
    out = []
    for key, src in srcs.items():
        if only and key != only:
            continue
        for f in src.get("files", []):
            p = folder / f["path"]
            if p.exists() and sha256(p) == f["sha256"]:
                out.append({"source": key, "path": f["path"], "action": "present"})
                continue
            if not f.get("url"):
                out.append({"source": key, "path": f["path"], "action": "no-url"})
                continue
            req = urllib.request.Request(f["url"], headers={"User-Agent": USER_AGENT})
            try:
                with urllib.request.urlopen(req, timeout=timeout) as r:
                    data = r.read()
            except (urllib.error.URLError, OSError) as e:
                out.append({"source": key, "path": f["path"], "action": "download-failed", "error": str(e)})
                continue
            got = hashlib.sha256(data).hexdigest()
            if got != f["sha256"]:
                out.append({"source": key, "path": f["path"], "action": "checksum-mismatch", "sha256": got})
                continue
            p.parent.mkdir(parents=True, exist_ok=True)
            atomic_write_bytes(p, data)
            out.append({"source": key, "path": f["path"], "action": "downloaded", "bytes": len(data)})
    return out
