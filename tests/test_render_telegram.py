from datetime import datetime, timezone
from pathlib import Path

from worker.models import Article, Candidate, Verdict
from worker.render import make_slug, write_digest
from worker.telegram import MAX_LEN, build_message

BASE = "https://example.github.io/tech-radar"
NOW = datetime(2026, 11, 24, tzinfo=timezone.utc)


def article(title="A <b> & B", url="https://example.com/x?a=1&b=2", summary="Tóm tắt & <script>"):
    c = Candidate(source="hn", title=title, url=url, published=NOW)
    return Article(
        candidate=c,
        verdict=Verdict(id=0, score=8, reason="r", topic="ai"),
        slug=make_slug(title, url),
        summary=summary,
        body_markdown="## Vấn đề\nChưa rõ.",
        quality="description",
    )


def test_slug_is_ascii_stable_and_unique_per_url():
    a = make_slug("Xin chào Việt Nam!", "https://a.example")
    assert a == make_slug("Xin chào Việt Nam!", "https://a.example")
    assert a.isascii()
    assert a != make_slug("Xin chào Việt Nam!", "https://b.example")


def test_message_escapes_html_and_links_both_pages():
    text = build_message("2026-11-24", [article()], BASE)
    assert "A &lt;b&gt; &amp; B" in text
    assert "&lt;script&gt;" in text
    assert "<script>" not in text
    assert 'href="https://example.com/x?a=1&amp;b=2"' in text
    assert f'href="{BASE}/digests/2026-11-24/' in text
    assert "Đào sâu" in text and "Nguồn gốc" in text


def test_message_stays_under_telegram_limit():
    many = [article(title=f"T{i} " + "x" * 200, summary="y" * 1000) for i in range(30)]
    text = build_message("2026-11-24", many, BASE)
    assert len(text) <= MAX_LEN


def test_write_digest_creates_index_and_pages(tmp_path: Path):
    target = write_digest("2026-11-24", [article()], docs_dir=tmp_path)
    assert (target / "index.md").exists()
    page = next(p for p in target.glob("*.md") if p.name != "index.md")
    assert page.read_text(encoding="utf-8").startswith("# A <b> & B")
    assert "[A <b> & B](" in (target / "index.md").read_text(encoding="utf-8")


def test_write_digest_overwrites_previous_run(tmp_path: Path):
    write_digest("2026-11-24", [article(title="old")], docs_dir=tmp_path)
    target = write_digest("2026-11-24", [article(title="new")], docs_dir=tmp_path)
    names = {p.name for p in target.glob("*.md")}
    assert len(names) == 2  # index + 1 bài, không còn bài cũ
