"""Ghi bài Markdown vào docs/digests/YYYY-MM-DD/ cho MkDocs."""

from __future__ import annotations

import hashlib
import re
import shutil
import unicodedata
from pathlib import Path

from .models import Article

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"


def make_slug(title: str, url: str) -> str:
    """Slug ASCII ổn định, thêm 6 ký tự hash từ URL để tránh trùng."""
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")[:50].strip("-") or "muc"
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:6]
    return f"{base}-{digest}"


def _article_page(article: Article, date: str) -> str:
    c = article.candidate
    return (
        f"# {c.title}\n\n"
        f"!!! info \"Nguồn\"\n"
        f"    Nguồn gốc: <{c.url}>\n"
        f"    Chất lượng phân tích: {article.quality}\n\n"
        f"{article.summary}\n\n"
        f"{article.body_markdown}\n"
    )


def _index_page(articles: list[Article], date: str) -> str:
    lines = [f"# Bản tin {date}", "", f"{len(articles)} mục được chọn tự động.", ""]
    for i, a in enumerate(articles, 1):
        summary = " ".join(a.summary.split())
        lines.append(f"{i}. [{a.candidate.title}]({a.slug}.md)  ")
        lines.append(f"   {summary}  ")
        lines.append(f"   [Nguồn gốc]({a.candidate.url})")
        lines.append("")
    return "\n".join(lines)


def write_digest(date: str, articles: list[Article], docs_dir: Path = DOCS_DIR) -> Path:
    """Ghi lại toàn bộ thư mục của ngày đó (ghi đè nếu chạy lại)."""
    target = docs_dir / "digests" / date
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    (target / "index.md").write_text(_index_page(articles, date), encoding="utf-8")
    for article in articles:
        (target / f"{article.slug}.md").write_text(_article_page(article, date), encoding="utf-8")
    return target
