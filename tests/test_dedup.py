from datetime import datetime, timedelta, timezone

from worker import dedup as dd
from worker.models import Candidate

NOW = datetime(2026, 11, 24, 0, 0, tzinfo=timezone.utc)


def cand(title, url, repo=None, when=NOW, source="hn"):
    return Candidate(source=source, title=title, url=url, published=when, repo=repo)


def test_canonical_url_strips_query_fragment_www_and_trailing_slash():
    assert dd.canonical_url("https://www.Example.com/a/b/?utm=1#x") == "example.com/a/b"


def test_canonical_url_keeps_identifying_query_params():
    a = dd.canonical_url("https://news.ycombinator.com/item?id=123")
    b = dd.canonical_url("https://news.ycombinator.com/item?id=456")
    assert a != b
    assert dd.canonical_url("https://youtube.com/watch?v=abc&utm_source=x") == "youtube.com/watch?v=abc"
    assert dd.canonical_url("https://x.com/p?b=2&a=1") == dd.canonical_url("https://x.com/p?a=1&b=2")


def test_github_repo_key_only_for_repo_root():
    assert dd.github_repo_key("https://github.com/Astral-sh/uv") == "repo:astral-sh/uv"
    assert dd.github_repo_key("https://github.com/astral-sh/uv/releases/tag/0.5.0") is None
    assert dd.github_repo_key("https://example.com/astral-sh/uv") is None


def test_same_repo_via_different_urls_is_one_item():
    a = cand("uv", "https://github.com/astral-sh/uv", source="github_search")
    b = cand("Show HN: uv", "https://github.com/astral-sh/uv/?ref=hn")
    kept = dd.dedup([a, b], dd.empty_state(), NOW)
    assert len(kept) == 1


def test_already_seen_item_is_skipped():
    state = dd.empty_state()
    first = cand("Some article", "https://example.com/post")
    dd.mark(state, [first], "published", NOW)
    again = cand("Some article", "https://example.com/post?ref=x")
    assert dd.dedup([again], state, NOW) == []


def test_near_duplicate_title_from_other_source_is_dropped():
    a = cand("PostgreSQL 18 released with async I/O", "https://a.example/pg18")
    b = cand("PostgreSQL 18 released with async I/O!", "https://b.example/pg18")
    assert len(dd.dedup([a, b], dd.empty_state(), NOW)) == 1


def test_distinct_titles_are_kept():
    a = cand("Rust 2.0 announced", "https://a.example/rust")
    b = cand("Kubernetes 1.40 release notes", "https://b.example/k8s")
    assert len(dd.dedup([a, b], dd.empty_state(), NOW)) == 2


def test_prune_removes_entries_older_than_retention():
    state = dd.empty_state()
    old = NOW - timedelta(days=dd.RETENTION_DAYS + 1)
    dd.mark(state, [cand("old", "https://old.example")], "rejected", old)
    dd.mark(state, [cand("new", "https://new.example")], "rejected", NOW)
    dd.prune(state, NOW)
    assert list(state["items"]) == ["url:new.example"]
