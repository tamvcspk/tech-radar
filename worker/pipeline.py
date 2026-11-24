"""Điều phối: ingest → dedup → chấm điểm → chọn → làm giàu → sinh bài → ghi docs + manifest."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from . import dedup as dd
from .article import write_article
from .config import ROOT, Settings
from .enrich import fetch_material
from .gatekeeper import score_candidates, select
from .ingest import fetch_all
from .llm import LLMProvider, TransientLLMError
from .render import write_digest
from .telegram import build_message, write_manifest

log = logging.getLogger(__name__)

LOOKBACK = timedelta(hours=24)
VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
ASSETS_DIR = ROOT / "assets"
STATE_PATH = ASSETS_DIR / "processed_urls.json"
OUT_DIR = ROOT / "out"
TELEGRAM_MANIFEST = "telegram.json"


def run_generate(
    settings: Settings,
    llm: LLMProvider,
    session: requests.Session,
    now: datetime | None = None,
) -> Path | None:
    """Trả về thư mục bản tin đã ghi, hoặc None nếu không có mục nào đạt ngưỡng."""
    now = now or datetime.now(timezone.utc)
    # Xóa manifest cũ để `send` không gửi lại tin của lần chạy trước khi hôm nay không có bài.
    (OUT_DIR / TELEGRAM_MANIFEST).unlink(missing_ok=True)
    state = dd.load_state(STATE_PATH)
    dd.prune(state, now, archive_dir=STATE_PATH.parent)

    raw = fetch_all(session, now - LOOKBACK, settings.github_token)
    fresh = dd.dedup(raw, state, now)
    log.info("Thu được %d mục, sau dedup còn %d", len(raw), len(fresh))
    if not fresh:
        dd.save_state(STATE_PATH, state)
        return None

    scored = score_candidates(fresh, llm)
    chosen = select(scored)
    log.info("Chấm điểm %d mục, chọn %d mục", len(scored), len(chosen))
    dd.mark(state, [s.candidate for s in scored if s not in chosen], "rejected", now)

    articles = []
    for item in chosen:
        candidate = item.candidate
        try:
            material, quality = fetch_material(candidate, session, settings.github_token)
            if not material.strip():
                raise ValueError("không có nội dung để phân tích")
            articles.append(write_article(candidate, item.verdict, material, quality, llm))
            dd.mark(state, [candidate], "published", now)
        except TransientLLMError as exc:
            # Lỗi tạm thời (rate limit/quá tải): không đánh dấu, để lần chạy sau thử lại.
            log.warning("Bỏ mục %s vì LLM lỗi tạm thời: %s", candidate.title, exc)
        except Exception as exc:  # noqa: BLE001 - một mục hỏng không làm hỏng cả bản tin
            log.warning("Bỏ mục %s: %s", candidate.title, exc)
            dd.mark(state, [candidate], "failed", now)

    dd.save_state(STATE_PATH, state)
    if not articles:
        return None

    date = now.astimezone(VN_TZ).date().isoformat()
    digest_dir = write_digest(date, articles)
    text = build_message(date, articles, settings.site_base_url)
    write_manifest(OUT_DIR / TELEGRAM_MANIFEST, date, text)
    return digest_dir
