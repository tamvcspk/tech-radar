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
            }
        ]
    }
    items = parse_github_search(payload, SINCE)
    assert len(items) == 1
    assert items[0].repo == "astral-sh/uv"
    assert items[0].source == "github_search"


def test_releases_atom_keeps_only_recent_entries():
    items = parse_releases_atom(ATOM, "python/cpython", SINCE)
    assert [i.title for i in items] == ["python/cpython v3.14.1"]
    assert items[0].url == "https://github.com/python/cpython/releases/tag/v3.14.1"
    assert items[0].repo is None
