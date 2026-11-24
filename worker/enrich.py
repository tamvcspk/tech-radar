"""Chặng 2a: lấy nội dung nguồn để LLM phân tích.

Thứ tự ưu tiên:
- Repo GitHub gốc: README, chỉ khi repo có license rõ ràng (kiểm tra trước khi tóm tắt).
- Bài viết/trang khác: trafilatura trích văn bản chính.
- Không lấy được gì: dùng mô tả từ feed và đánh dấu chất lượng "description".
"""

from __future__ import annotations

import logging

import requests

from .ingest import TIMEOUT, _gh_headers
from .models import Candidate, Quality

log = logging.getLogger(__name__)

MAX_CHARS = 15000


def _github_readme(repo: str, session: requests.Session, token: str) -> str | None:
    meta = session.get(f"https://api.github.com/repos/{repo}", headers=_gh_headers(token), timeout=TIMEOUT)
    meta.raise_for_status()
    spdx = ((meta.json().get("license") or {}).get("spdx_id") or "").strip()
    if not spdx or spdx == "NOASSERTION":
        log.info("Repo %s không có license rõ ràng, không dùng README", repo)
        return None

    readme = session.get(
        f"https://api.github.com/repos/{repo}/readme",
        headers={**_gh_headers(token), "Accept": "application/vnd.github.raw"},
        timeout=TIMEOUT,
    )
    if readme.status_code == 404:
        return None
    readme.raise_for_status()
    return readme.text


def _web_text(url: str) -> str | None:
    import trafilatura

    html = trafilatura.fetch_url(url)
    if not html:
        return None
    return trafilatura.extract(html, include_comments=False, include_tables=True)


def fetch_material(candidate: Candidate, session: requests.Session, token: str) -> tuple[str, Quality]:
    """Trả về (văn bản nguồn, chất lượng). Văn bản có thể rỗng nếu không có gì để phân tích."""
    try:
        if candidate.repo:
            text = _github_readme(candidate.repo, session, token)
            if text and text.strip():
                return text[:MAX_CHARS], "readme"
        else:
            text = _web_text(candidate.url)
            if text and text.strip():
                return text[:MAX_CHARS], "fulltext"
    except Exception as exc:  # noqa: BLE001 - lỗi lấy nội dung không làm hỏng mục khác
        log.warning("Không lấy được nội dung của %s: %s", candidate.url, exc)

    log.info("Dùng mô tả ngắn cho %s", candidate.url)
    return candidate.description, "description"
