"""CLI: `python -m worker run` sinh bản tin; `python -m worker send` gửi Telegram."""

from __future__ import annotations

import argparse
import logging
import sys

import requests

from .config import Settings
from .llm import GeminiProvider
from .pipeline import OUT_DIR, TELEGRAM_MANIFEST, run_generate
from .telegram import send_from_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="worker")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run", help="Lấy tin, chấm điểm, sinh Markdown và manifest Telegram")
    send = sub.add_parser("send", help="Gửi manifest Telegram (chạy sau khi Pages đã deploy)")
    send.add_argument(
        "--dry-run",
        action="store_true",
        help="In tin ra console thay vì gửi (bật mặc định nếu DRY_RUN=1)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    settings = Settings.load()

    if args.command == "run":
        if not settings.gemini_api_key:
            print("Thiếu GEMINI_API_KEY", file=sys.stderr)
            return 2
        llm = GeminiProvider(settings.gemini_api_key, settings.gemini_model)
        session = requests.Session()
        digest_dir = run_generate(settings, llm, session)
        print(f"Đã sinh bản tin: {digest_dir or 'không có mục nào đạt ngưỡng'}")
        return 0

    dry_run = args.dry_run or settings.dry_run
    return send_from_manifest(settings, OUT_DIR / TELEGRAM_MANIFEST, dry_run=dry_run)


if __name__ == "__main__":
    sys.exit(main())
