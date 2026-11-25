"""Dedup và trạng thái (assets/processed_urls.json + xoay vòng file nén .json.gz theo tháng).

Khóa nhận diện một mục:
- URL chuẩn hóa (bỏ fragment, www, dấu / cuối, tham số tracking; giữ các query param còn lại như ?id=, ?v=).
- Với repo GitHub gốc (đúng 2 đoạn path): thêm khóa "repo:owner/name".
- Tiêu đề gần giống (>= 0.85) với mục đã thấy trong 7 ngày gần nhất.
"""

from __future__ import annotations

import gzip
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit

from .models import Candidate

RETENTION_DAYS = 60
MAX_ACTIVE_ITEMS = 5000  # trần số khóa trong file hiện hành để không phình vô hạn
MAX_ARCHIVE_FILES = 12  # giữ tối đa 12 file nén theo tháng (1 năm)
TITLE_WINDOW_DAYS = 7
TITLE_SIMILARITY = 0.85
ARCHIVE_PREFIX = "processed_urls-"
ARCHIVE_SUFFIX = ".json.gz"


TRACKING_PARAMS = {"utm", "ref", "ref_src", "fbclid", "gclid", "mc_cid", "mc_eid", "igshid"}


def _is_tracking_param(name: str) -> bool:
    name = name.lower()
    return name.startswith("utm_") or name in TRACKING_PARAMS


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    host = parts.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    kept_params = [
        (k, v)
        for k, v in sorted(parse_qsl(parts.query, keep_blank_values=True))
        if not _is_tracking_param(k)
    ]
    query = urlencode(kept_params)
    base = f"{host}{parts.path.rstrip('/')}"
    return f"{base}?{query}" if query else base


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


def _dump_compact(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_dump_compact(state), encoding="utf-8")


def load_last_sent(path: Path) -> str | None:
    """Ngày (YYYY-MM-DD, giờ ICT) của bản tin đã gửi Telegram gần nhất, hoặc None."""
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8").strip() or None


def save_last_sent(path: Path, date: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(date + "\n", encoding="utf-8")


def since_for(state: dict, now: datetime, default: timedelta, cap: timedelta) -> datetime:
    """Mốc bắt đầu lấy tin: lần chạy thành công gần nhất, kẹp trong [now - cap, now].

    Chưa có lần chạy nào (hoặc giá trị hỏng) thì lùi `default` so với now.
    """
    raw = state.get("last_success_at")
    if raw:
        try:
            last = datetime.fromisoformat(raw)
        except ValueError:
            last = None
        if last is not None:
            if last.tzinfo is None:
                last = last.replace(tzinfo=timezone.utc)
            return min(max(last, now - cap), now)
    return now - default


def _archive_expired(expired: dict[str, dict], archive_dir: Path, max_archives: int) -> None:
    """Xoay vòng mục hết hạn vào file nén processed_urls-YYYY-MM.json.gz và giới hạn số file lưu."""
    if not expired:
        return
    archive_dir.mkdir(parents=True, exist_ok=True)
    by_month: dict[str, dict[str, dict]] = defaultdict(dict)
    for key, entry in expired.items():
        seen = datetime.fromisoformat(entry["seen_at"]).astimezone(timezone.utc)
        by_month[seen.strftime("%Y-%m")][key] = entry

    for month, entries in by_month.items():
        archive_path = archive_dir / f"{ARCHIVE_PREFIX}{month}{ARCHIVE_SUFFIX}"
        existing = empty_state()
        if archive_path.exists():
            existing = json.loads(gzip.decompress(archive_path.read_bytes()).decode("utf-8"))
        existing["items"].update(entries)
        # mtime=0 để output gzip quyết định (deterministic), tránh diff thừa trong git.
        compressed = gzip.compress(_dump_compact(existing).encode("utf-8"), compresslevel=9, mtime=0)
        archive_path.write_bytes(compressed)

    archives = sorted(archive_dir.glob(f"{ARCHIVE_PREFIX}*{ARCHIVE_SUFFIX}"))
    for old in archives[: max(0, len(archives) - max_archives)]:
        old.unlink(missing_ok=True)


def prune(
    state: dict,
    now: datetime,
    archive_dir: Path | None = None,
    max_active: int = MAX_ACTIVE_ITEMS,
    max_archives: int = MAX_ARCHIVE_FILES,
) -> None:
    """Loại mục quá hạn hoặc vượt trần; nếu có archive_dir thì xoay vòng sang file .json.gz."""
    cutoff = now - timedelta(days=RETENTION_DAYS)
    kept: dict[str, dict] = {}
    expired: dict[str, dict] = {}
    for key, entry in state["items"].items():
        if datetime.fromisoformat(entry["seen_at"]) >= cutoff:
            kept[key] = entry
        else:
            expired[key] = entry

    if len(kept) > max_active:
        ordered = sorted(kept.items(), key=lambda kv: datetime.fromisoformat(kv[1]["seen_at"]), reverse=True)
        kept = dict(ordered[:max_active])
        expired.update(ordered[max_active:])

    if archive_dir is not None:
        _archive_expired(expired, archive_dir, max_archives=max_archives)
    state["items"] = kept


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
