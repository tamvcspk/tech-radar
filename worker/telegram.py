"""Tạo tin Telegram (parse_mode=HTML) và gửi qua Bot API."""

from __future__ import annotations

import html
import json
import logging
from pathlib import Path

import requests

from .config import Settings
from .models import Article

log = logging.getLogger(__name__)

MAX_LEN = 4096
TITLE_MAX = 150
SUMMARY_MAX = 300


def _esc(text: str) -> str:
    return html.escape(text, quote=False)


def _esc_attr(url: str) -> str:
    return html.escape(url, quote=True)


def _trim(text: str, limit: int) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


def build_message(date: str, articles: list[Article], site_base_url: str) -> str:
    """Tin 1 lần/ngày. Nếu quá 4096 ký tự thì bỏ bớt mục cuối, không cắt giữa thẻ HTML."""
    text = f"<b>Tech Radar · {_esc(date)}</b>"
    for i, a in enumerate(articles, 1):
        page = f"{site_base_url}/digests/{date}/{a.slug}/"
        block = (
            f"\n\n<b>{i}. {_esc(_trim(a.candidate.title, TITLE_MAX))}</b>\n"
            f"{_esc(_trim(a.summary, SUMMARY_MAX))}\n"
            f'<a href="{_esc_attr(page)}">Đào sâu</a> · '
            f'<a href="{_esc_attr(a.candidate.url)}">Nguồn gốc</a>'
        )
        if len(text) + len(block) > MAX_LEN:
            log.warning("Tin Telegram vượt %d ký tự, bỏ mục %d trở đi", MAX_LEN, i)
            break
        text += block
    return text


def write_manifest(path: Path, date: str, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"date": date, "text": text}, ensure_ascii=False, indent=2), encoding="utf-8")


def send_message(settings: Settings, text: str, dry_run: bool) -> bool:
    if dry_run:
        print("--- DRY RUN: tin sẽ gửi ---")
        print(text)
        print("--- hết ---")
        return True

    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        raise RuntimeError("Thiếu TELEGRAM_BOT_TOKEN hoặc TELEGRAM_CHAT_ID")
    resp = requests.post(
        f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
        json={
            "chat_id": settings.telegram_chat_id,
            "text": text,
            "parse_mode": "HTML",
            "link_preview_options": {"is_disabled": True},
        },
        timeout=20,
    )
    resp.raise_for_status()
    return bool(resp.json().get("ok"))


def send_from_manifest(settings: Settings, manifest: Path, dry_run: bool) -> int:
    if not manifest.exists():
        print("Không có manifest Telegram, bỏ qua (ngày không có mục nào đạt ngưỡng).")
        return 0
    data = json.loads(manifest.read_text(encoding="utf-8"))
    ok = send_message(settings, data["text"], dry_run=dry_run)
    return 0 if ok else 1
