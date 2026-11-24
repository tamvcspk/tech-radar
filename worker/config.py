"""Đọc cấu hình từ biến môi trường, và từ .env khi chạy local.

Biến môi trường thật luôn thắng .env (dùng setdefault).
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_GEMINI_MODEL = "gemini-3.8-flash"
DEFAULT_SITE_BASE_URL = "https://tamvcspk.github.io/tech-radar"


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip().removeprefix("export ").strip()
        value = value.strip()
        if value[:1] in {'"', "'"} and value.find(value[0], 1) != -1:
            value = value[1 : value.find(value[0], 1)]  # bỏ dấu ngoặc và phần comment sau đó
        else:
            value = re.split(r"\s#", value, maxsplit=1)[0].strip()
        os.environ.setdefault(key, value)


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    telegram_bot_token: str
    telegram_chat_id: str
    dry_run: bool
    github_token: str
    site_base_url: str

    @classmethod
    def load(cls) -> "Settings":
        load_dotenv(ROOT / ".env")
        env = os.environ.get
        return cls(
            gemini_api_key=env("GEMINI_API_KEY", "").strip(),
            gemini_model=env("GEMINI_MODEL", DEFAULT_GEMINI_MODEL).strip() or DEFAULT_GEMINI_MODEL,
            telegram_bot_token=env("TELEGRAM_BOT_TOKEN", "").strip(),
            telegram_chat_id=env("TELEGRAM_CHAT_ID", "").strip(),
            # Mặc định an toàn: không gửi Telegram khi chưa chủ động tắt DRY_RUN.
            dry_run=env("DRY_RUN", "1").strip().lower() in {"1", "true", "yes"},
            github_token=env("GITHUB_TOKEN", "").strip(),
            site_base_url=env("SITE_BASE_URL", DEFAULT_SITE_BASE_URL).strip().rstrip("/"),
        )
