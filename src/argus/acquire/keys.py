"""API keys: read from the environment or a git-ignored file, never printed or logged."""
from __future__ import annotations

import os
import re
from pathlib import Path

KEY_FILE = "OPENALEX_API_KEY.txt"
ENV = "OPENALEX_API_KEY"


class MissingKey(RuntimeError):
    pass


def openalex_key(root: Path) -> str:
    key = os.environ.get(ENV, "").strip()
    if not key and (root / KEY_FILE).exists():
        key = (root / KEY_FILE).read_text(encoding="utf-8").strip()
    if not key:
        raise MissingKey(f"no OpenAlex API key: set {ENV} or put it in {KEY_FILE} (git-ignored)")
    return key


def redact(text: str, *secrets: str) -> str:
    """Remove secrets (and any api_key=... parameter) from text before it is shown or stored."""
    for s in secrets:
        if s:
            text = text.replace(s, "<redacted>")
    return re.sub(r"(api_key=)[^&\s]+", r"\1<redacted>", text)
