from datetime import datetime, timezone

from worker.ingest import parse_github_search, parse_hn_feed, parse_releases_atom

SINCE = datetime(2026, 11, 23, 0, 0, tzinfo=timezone.utc)

HN_RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
<item>
  <title>Big launch</title>
  <link>https://example.com/big</link>
  <pubDate>Mon, 24 Nov 2026 01:00:00 GMT</pubDate>
  <description>&lt;p&gt;Points: 412&lt;/p&gt;&lt;p&gt;# Comments: 80&lt;/p&gt;</description>
</item>
<item>
  <title>Too old</title>
  <link>https://example.com/old</link>
  <pubDate>Fri, 20 Nov 2026 01:00:00 GMT</pubDate>
  <description>Points: 999</description>
</item>
</channel></rss>
"""

ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>v3.14.1</title>
    <link rel="alternate" href="https://github.com/python/cpython/releases/tag/v3.14.1"/>
    <updated>2026-11-24T03:00:00Z</updated>
  </entry>
  <entry>
    <title>v3.13.0</title>
    <link rel="alternate" href="https://github.com/python/cpython/releases/tag/v3.13.0"/>
    <updated>2026-10-01T03:00:00Z</updated>
  </entry>
</feed>
"""


def test_hn_feed_parses_points_and_filters_by_time():
    items = parse_hn_feed(HN_RSS, SINCE)
    assert [i.title for i in items] == ["Big launch"]
    assert items[0].points == 412
    assert items[0].source == "hn"


def test_github_search_parses_repo_items():
    payload = {
        "items": [
            {
                "full_name": "astral-sh/uv",
                "html_url": "https://github.com/astral-sh/uv",
                "description": "Python packaging",
                "created_at": "2026-11-23T12:00:00Z",
                "fork": False,
                "archived": False,
                "license": {"spdx_id": "MIT"},
            }
        ]
    }
    items = parse_github_search(payload, SINCE)
    assert len(items) == 1
    assert items[0].repo == "astral-sh/uv"
    assert items[0].source == "github_search"


def test_github_search_drops_forks_unlicensed_and_suspicious_repos():
    base = {"created_at": "2026-11-23T12:00:00Z", "fork": False, "archived": False, "license": {"spdx_id": "MIT"}}
    payload = {
        "items": [
            {**base, "full_name": "a/fork", "html_url": "https://github.com/a/fork", "description": "x", "fork": True},
            {**base, "full_name": "a/nolic", "html_url": "https://github.com/a/nolic", "description": "x", "license": None},
            {**base, "full_name": "b/fisch-script", "html_url": "https://github.com/b/fisch-script", "description": ""},
            {**base, "full_name": "c/tool", "html_url": "https://github.com/c/tool", "description": "Free Solana sniper bot"},
            {**base, "full_name": "d/good", "html_url": "https://github.com/d/good", "description": "Fast parser"},
        ]
    }
    items = parse_github_search(payload, SINCE)
    assert [i.repo for i in items] == ["d/good"]


def test_hn_feed_sets_repo_for_github_links_and_drops_boilerplate_description():
    rss = HN_RSS.replace("https://example.com/big", "https://github.com/owner/proj?ref=hn#readme")
    item = parse_hn_feed(rss, SINCE)[0]
    assert item.repo == "owner/proj"
    assert item.description == ""  # chỉ có Points/# Comments nên không có mô tả thật


def test_github_repo_from_url_handles_query_fragment_git_suffix_and_non_repos():
    from worker.ingest import github_repo_from_url

    assert github_repo_from_url("https://github.com/astral-sh/uv?tab=readme-ov-file") == "astral-sh/uv"
    assert github_repo_from_url("https://www.github.com/astral-sh/uv.git#readme") == "astral-sh/uv"
    assert github_repo_from_url("https://github.com/topics/python") is None
    assert github_repo_from_url("https://github.com/astral-sh/uv/releases/tag/0.5.0") is None


def test_hn_feed_treats_naive_pubdate_as_utc():
    rss = HN_RSS.replace("Mon, 24 Nov 2026 01:00:00 GMT", "Mon, 24 Nov 2026 01:00:00 -0000")
    assert len(parse_hn_feed(rss, SINCE)) == 1


def test_github_search_drops_noassertion_license():
    item = {
        "full_name": "a/b", "html_url": "https://github.com/a/b", "description": "x",
        "created_at": "2026-11-23T12:00:00Z", "fork": False, "archived": False,
        "license": {"spdx_id": "NOASSERTION"},
    }
    assert parse_github_search({"items": [item]}, SINCE) == []


def test_suspicious_filter_uses_word_boundaries():
    from worker.ingest import is_suspicious_repo

    assert not is_suspicious_repo("a/hackathon-starter", "Hackernews cheatsheet")
    assert not is_suspicious_repo("a/task-executor", "Thread pool executor")
    assert is_suspicious_repo("a/game-hack", "")
    assert is_suspicious_repo("a/tool", "Roblox executor")


def test_releases_atom_skips_prerelease_and_empty_href_and_reads_content():
    atom = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry><title>v16.5.0-canary.62</title>
    <link href="https://github.com/vercel/next.js/releases/tag/v16.5.0-canary.62"/>
    <updated>2026-11-24T03:00:00Z</updated></entry>
  <entry><title>empty</title><link href=""/><updated>2026-11-24T03:00:00Z</updated></entry>
  <entry><title>v1.2.0</title>
    <link href="https://github.com/a/b/releases/tag/v1.2.0"/>
    <updated>2026-11-24T03:00:00Z</updated>
    <content type="html">&lt;p&gt;Faster &amp;amp; smaller&lt;/p&gt;</content></entry>
</feed>"""
    items = parse_releases_atom(atom, "a/b", SINCE)
    assert [i.title for i in items] == ["a/b v1.2.0"]
    assert items[0].description == "Faster & smaller"


def test_releases_atom_keeps_only_recent_entries():
    items = parse_releases_atom(ATOM, "python/cpython", SINCE)
    assert [i.title for i in items] == ["python/cpython v3.14.1"]
    assert items[0].url == "https://github.com/python/cpython/releases/tag/v3.14.1"
    assert items[0].repo is None


def test_releases_atom_skips_cpython_and_go_style_prereleases():
    atom = """<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry><title>v3.14.0a7</title><link href="https://github.com/python/cpython/releases/tag/v3.14.0a7"/><updated>2026-11-24T03:00:00Z</updated></entry>
  <entry><title>v3.14.0b1</title><link href="https://github.com/python/cpython/releases/tag/v3.14.0b1"/><updated>2026-11-24T03:00:00Z</updated></entry>
  <entry><title>v3.14.0rc1</title><link href="https://github.com/python/cpython/releases/tag/v3.14.0rc1"/><updated>2026-11-24T03:00:00Z</updated></entry>
  <entry><title>go1.24rc1</title><link href="https://github.com/golang/go/releases/tag/go1.24rc1"/><updated>2026-11-24T03:00:00Z</updated></entry>
  <entry><title>go1.24.0</title><link href="https://github.com/golang/go/releases/tag/go1.24.0"/><updated>2026-11-24T03:00:00Z</updated></entry>
</feed>"""
    items = parse_releases_atom(atom, "golang/go", SINCE)
    assert [i.title for i in items] == ["golang/go go1.24.0"]
