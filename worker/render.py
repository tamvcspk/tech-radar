"""Ghi bài Markdown vào docs/digests/YYYY-MM-DD/ cho MkDocs."""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path

from .models import Article

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
# File dotfile nên MkDocs bỏ qua. Lưu các bài của ngày để chạy lại không làm mất bài cũ.
STATE_FILE = ".articles.json"
DATE_DIR = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def make_slug(title: str, url: str) -> str:
    """Slug ASCII ổn định, thêm 6 ký tự hash từ URL để tránh trùng."""
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    base = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")[:50].strip("-") or "muc"
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:6]
    return f"{base}-{digest}"


def _link_text(text: str) -> str:
    """Escape ký tự làm vỡ cú pháp link Markdown trong phần text."""
    return re.sub(r"([\[\]\\])", r"\\\1", " ".join(text.split()))


def _link_url(url: str) -> str:
    """Mã hóa khoảng trắng và ngoặc đơn để URL không đóng link sớm."""
    return url.strip().replace(" ", "%20").replace("(", "%28").replace(")", "%29")


def _article_page(article: Article) -> str:
    c = article.candidate
    return (
        f"# {c.title}\n\n"
        f'!!! info "Nguồn"\n'
        f"    Nguồn gốc: <{c.url}>\n\n"
        f"    Chất lượng phân tích: {article.quality}\n\n"
        f"{article.summary}\n\n"
        f"{article.body_markdown}\n"
    )


def _index_page(articles: list[Article], date: str) -> str:
    lines = [f"# Bản tin {date}", "", f"{len(articles)} mục được chọn tự động.", ""]
    for i, a in enumerate(articles, 1):
        summary = " ".join(a.summary.split())
        lines.append(f"{i}. [{_link_text(a.candidate.title)}]({a.slug}.md)  ")
        lines.append(f"   {summary}  ")
        lines.append(f"   [Nguồn gốc]({_link_url(a.candidate.url)})")
        lines.append("")
    return "\n".join(lines)


def _load_existing(target: Path) -> list[Article]:
    state = target / STATE_FILE
    if not state.exists():
        return []
    try:
        items = json.loads(state.read_text(encoding="utf-8"))
        articles = [Article.model_validate(item) for item in items]
    except (ValueError, TypeError):
        return []
    return [a for a in articles if (target / f"{a.slug}.md").exists()]


def write_archive_index(docs_dir: Path = DOCS_DIR) -> Path:
    """Cập nhật docs/digests/index.md liệt kê các ngày theo thứ tự mới nhất trước."""
    digests_dir = docs_dir / "digests"
    digests_dir.mkdir(parents=True, exist_ok=True)
    dates = sorted(
        (p.name for p in digests_dir.iterdir() if p.is_dir() and DATE_DIR.match(p.name) and (p / "index.md").exists()),
        reverse=True,
    )
    lines = ["# Kho bản tin", "", "Danh sách bản tin hằng ngày, mới nhất ở trên cùng.", ""]
    for date in dates:
        lines.append(f"- [{date}]({date}/index.md)")
    lines.append("")
    index_path = digests_dir / "index.md"
    index_path.write_text("\n".join(lines), encoding="utf-8")
    return index_path


def write_digest(date: str, articles: list[Article], docs_dir: Path = DOCS_DIR) -> Path:
    """Ghi bài của ngày. Chạy lại cùng ngày thì gộp với bài đã có (trùng slug thì bản mới thắng).

    Không xóa bài cũ: link Telegram đã gửi trước đó vẫn phải hoạt động.
    """
    target = docs_dir / "digests" / date
    target.mkdir(parents=True, exist_ok=True)

    merged = {a.slug: a for a in _load_existing(target)}
    for article in articles:
        merged[article.slug] = article
    all_articles = list(merged.values())

    for article in articles:
        (target / f"{article.slug}.md").write_text(_article_page(article), encoding="utf-8")
    (target / "index.md").write_text(_index_page(all_articles, date), encoding="utf-8")
    (target / STATE_FILE).write_text(
        json.dumps([a.model_dump(mode="json") for a in all_articles], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_archive_index(docs_dir)
    return target
