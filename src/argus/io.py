"""File I/O helpers: atomic writes, YAML with stable formatting, legacy CSV dialect."""
from __future__ import annotations

import csv
import io
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable, Sequence

import yaml


# --------------------------------------------------------------------------- atomic writes

def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write via a temp file in the same folder + os.replace (no torn files)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def atomic_write_text(path: Path, text: str, encoding: str = "utf-8") -> None:
    atomic_write_bytes(path, text.encode(encoding))


# --------------------------------------------------------------------------- YAML

class _Loader(yaml.SafeLoader):
    """SafeLoader that keeps dates as strings (log dates must stay '2026-10-13')."""


_Loader.yaml_implicit_resolvers = {
    ch: [(tag, rx) for tag, rx in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for ch, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


class _Dumper(yaml.SafeDumper):
    pass


def _str_representer(dumper: yaml.SafeDumper, data: str):
    style = "|" if "\n" in data else None
    return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=style)


_Dumper.add_representer(str, _str_representer)


def load_yaml(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return yaml.load(f, Loader=_Loader)


def dump_yaml(obj: Any, header: str = "") -> str:
    body = yaml.dump(
        obj,
        Dumper=_Dumper,
        sort_keys=False,
        allow_unicode=True,
        width=1_000_000,  # no folding: one field per line keeps diffs readable
        default_flow_style=False,
    )
    return (header + body) if header else body


# --------------------------------------------------------------------------- JSONL / CSV

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def jsonl_text(rows: Iterable[dict[str, Any]]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)


def csv_bytes(rows: Iterable[dict[str, Any]], fieldnames: Sequence[str], bom: bool = True) -> bytes:
    """CSV in the dialect the published deliverables have always used:
    utf-8 with BOM, CRLF line endings, minimal quoting, unknown keys ignored."""
    buf = io.StringIO(newline="")
    w = csv.DictWriter(buf, fieldnames=list(fieldnames), extrasaction="ignore")
    w.writeheader()
    for r in rows:
        w.writerow(r)
    return buf.getvalue().encode("utf-8-sig" if bom else "utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
