"""Dedup và trạng thái (processed_urls.json).

Khóa nhận diện một mục:
- URL chuẩn hóa (bỏ query, fragment, www, dấu / cuối).
- Với repo GitHub gốc (đúng 2 đoạn path): thêm khóa "repo:owner/name".
- Tiêu đề gần giống (>= 0.85) với mục đã thấy trong 7 ngày gần nhất.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import urlsplit

from .models import Candidate

RETENTION_DAYS = 60
TITLE_WINDOW_DAYS = 7
TITLE_SIMILARITY = 0.85


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    return f"{host}{parts.path.rstrip('/')}"


def github_repo_key(url: str) -> str | None:
    parts = urlsplit(url.strip())
    if parts.netloc.lower().removeprefix("www.") != "github.com":
        return None
    segments = [s for s in parts.path.split("/") if s]
    if len(segments) != 2:  # chỉ repo gốc, không phải release/issue/file
        return None
    return f"repo:{segments[0].lower()}/{segments[1].lower()}"


def keys_for(candidate: Candidate) -> set[str]:
    keys = {f"url:{canonical_url(candidate.url)}"}
    repo_key = github_repo_key(candidate.url)
    if repo_key:
        keys.add(repo_key)
    return keys


def empty_state() -> dict:
    return {"version": 1, "items": {}}


def load_state(path: Path) -> dict:
    if not path.exists():
        return empty_state()
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def prune(state: dict, now: datetime) -> None:
    cutoff = now - timedelta(days=RETENTION_DAYS)
    state["items"] = {
        key: entry
        for key, entry in state["items"].items()
        if datetime.fromisoformat(entry["seen_at"]) >= cutoff
    }


def _recent_titles(state: dict, now: datetime) -> list[str]:
    cutoff = now - timedelta(days=TITLE_WINDOW_DAYS)
    return [
        entry["title"]
        for entry in state["items"].values()
        if datetime.fromisoformat(entry["seen_at"]) >= cutoff
    ]


def _similar(a: str, b: str) -> bool:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio() >= TITLE_SIMILARITY


def dedup(candidates: list[Candidate], state: dict, now: datetime) -> list[Candidate]:
    """Trả về các mục chưa từng thấy và không trùng nhau trong lần chạy này."""
    known_keys = set(state["items"])
    recent_titles = _recent_titles(state, now)
    kept: list[Candidate] = []
    kept_keys: set[str] = set()
    kept_titles: list[str] = []

    for candidate in sorted(candidates, key=lambda c: c.published, reverse=True):
        keys = keys_for(candidate)
        if keys & known_keys or keys & kept_keys:
            continue
        title = candidate.title
        if any(_similar(title, t) for t in recent_titles + kept_titles):
            continue
        kept.append(candidate)
        kept_keys |= keys
        kept_titles.append(title)
    return kept


def mark(state: dict, candidates: list[Candidate], status: str, now: datetime) -> None:
    """Ghi trạng thái để lần sau không xét lại. status: published | rejected | failed."""
    for candidate in candidates:
        for key in keys_for(candidate):
            state["items"][key] = {
                "title": candidate.title,
                "seen_at": now.isoformat(),
                "status": status,
            }
