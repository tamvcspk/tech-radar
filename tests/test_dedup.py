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


def test_save_state_writes_compact_json_and_creates_parent(tmp_path):
    state = dd.empty_state()
    dd.mark(state, [cand("A", "https://a.example")], "published", NOW)
    target = tmp_path / "assets" / "processed_urls.json"
    dd.save_state(target, state)
    raw = target.read_text(encoding="utf-8")
    assert len(raw.splitlines()) == 1  # JSON nén gọn trên 1 dòng
    assert dd.load_state(target) == state


def test_prune_rotates_expired_entries_to_gzip_and_merges_same_month(tmp_path):
    import gzip
    import json

    old1 = datetime(2026, 8, 10, 0, 0, tzinfo=timezone.utc)
    old2 = datetime(2026, 8, 20, 0, 0, tzinfo=timezone.utc)

    state = dd.empty_state()
    dd.mark(state, [cand("old1", "https://old1.example")], "rejected", old1)
    dd.mark(state, [cand("new", "https://new.example")], "published", NOW)
    dd.prune(state, NOW, archive_dir=tmp_path)
    assert list(state["items"]) == ["url:new.example"]

    # Xoay vòng lần 2 cùng tháng phải gộp vào file cũ, không mất dữ liệu trước đó.
    dd.mark(state, [cand("old2", "https://old2.example")], "rejected", old2)
    dd.prune(state, NOW, archive_dir=tmp_path)

    archive = tmp_path / "processed_urls-2026-08.json.gz"
    assert archive.exists()
    data = json.loads(gzip.decompress(archive.read_bytes()).decode("utf-8"))
    assert sorted(data["items"]) == ["url:old1.example", "url:old2.example"]


def test_prune_caps_active_items_and_archive_count(tmp_path):
    state = dd.empty_state()
    for i in range(4):
        when = NOW - timedelta(hours=i)
        dd.mark(state, [cand(f"t{i}", f"https://ex{i}.example")], "rejected", when)
    dd.prune(state, NOW, archive_dir=tmp_path, max_active=2, max_archives=2)
    assert sorted(state["items"]) == ["url:ex0.example", "url:ex1.example"]

    # Tạo thêm 3 tháng cũ để kiểm tra giới hạn max_archives=2.
    for month in (1, 2, 3):
        old = datetime(2026, month, 15, tzinfo=timezone.utc)
        dd.mark(state, [cand(f"m{month}", f"https://m{month}.example")], "rejected", old)
    dd.prune(state, NOW, archive_dir=tmp_path, max_active=2, max_archives=2)
    archives = sorted(p.name for p in tmp_path.glob("processed_urls-*.json.gz"))
    assert len(archives) == 2
    assert archives == ["processed_urls-2026-03.json.gz", "processed_urls-2026-11.json.gz"]


def test_since_for_defaults_when_no_previous_run():
    now = datetime(2026, 11, 26, 1, 0, tzinfo=timezone.utc)
    since = dd.since_for(dd.empty_state(), now, timedelta(hours=24), timedelta(hours=72))
    assert since == now - timedelta(hours=24)


def test_since_for_uses_last_success_within_cap():
    now = datetime(2026, 11, 26, 1, 0, tzinfo=timezone.utc)
    state = {"items": {}, "last_success_at": (now - timedelta(hours=30)).isoformat()}
    assert dd.since_for(state, now, timedelta(hours=24), timedelta(hours=72)) == now - timedelta(hours=30)


def test_since_for_caps_at_72h_and_ignores_future_or_garbage():
    now = datetime(2026, 11, 26, 1, 0, tzinfo=timezone.utc)
    cap, default = timedelta(hours=72), timedelta(hours=24)
    old = {"items": {}, "last_success_at": (now - timedelta(days=10)).isoformat()}
    assert dd.since_for(old, now, default, cap) == now - cap
    future = {"items": {}, "last_success_at": (now + timedelta(hours=5)).isoformat()}
    assert dd.since_for(future, now, default, cap) == now
    garbage = {"items": {}, "last_success_at": "không phải ngày"}
    assert dd.since_for(garbage, now, default, cap) == now - default


def test_last_sent_roundtrip(tmp_path):
    path = tmp_path / "assets" / "last_sent_date"
    assert dd.load_last_sent(path) is None
    dd.save_last_sent(path, "2026-11-26")
    assert dd.load_last_sent(path) == "2026-11-26"
