"""Lấy mục mới từ 3 nguồn: hnrss (HN), GitHub Search API, GitHub Releases .atom.

Mỗi nguồn lỗi thì chỉ bỏ nguồn đó, không làm hỏng cả lần chạy.
"""

from __future__ import annotations

import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests

from .models import Candidate
from .sources import MIN_GH_STARS, MIN_HN_POINTS, WATCHED_REPOS

log = logging.getLogger(__name__)

TIMEOUT = 20
USER_AGENT = "tech-radar-bot/1.0"
HN_FEED = "https://hnrss.org/newest?points={points}"
GH_SEARCH = "https://api.github.com/search/repositories"
ATOM = "{http://www.w3.org/2005/Atom}"


def _gh_headers(token: str) -> dict[str, str]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def parse_hn_feed(xml_text: str, since: datetime) -> list[Candidate]:
    root = ET.fromstring(xml_text)
    out: list[Candidate] = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = item.findtext("pubDate")
        if not title or not link or not pub:
            continue
        published = parsedate_to_datetime(pub)
        if published < since:
            continue
        desc_html = item.findtext("description") or ""
        match = re.search(r"Points:\s*(\d+)", desc_html)
        text = " ".join(re.sub(r"<[^>]+>", " ", desc_html).split())
        out.append(
            Candidate(
                source="hn",
                title=title,
                url=link,
                description=text[:500],
                published=published,
                points=int(match.group(1)) if match else None,
            )
        )
    return out


def parse_github_search(payload: dict, since: datetime) -> list[Candidate]:
    out: list[Candidate] = []
    for item in payload.get("items", []):
        published = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        if published < since:
            continue
        out.append(
            Candidate(
                source="github_search",
                title=item["full_name"],
                url=item["html_url"],
                description=(item.get("description") or "")[:500],
                published=published,
                repo=item["full_name"],
            )
        )
    return out


def parse_releases_atom(xml_text: str, repo: str, since: datetime) -> list[Candidate]:
    root = ET.fromstring(xml_text)
    out: list[Candidate] = []
    for entry in root.findall(f"{ATOM}entry"):
        title = (entry.findtext(f"{ATOM}title") or "").strip()
        link_el = entry.find(f"{ATOM}link")
        updated = entry.findtext(f"{ATOM}updated")
        if not title or link_el is None or not updated:
            continue
        published = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        if published < since:
            continue
        out.append(
            Candidate(
                source="github_release",
                title=f"{repo} {title}",
                url=link_el.get("href", ""),
                published=published,
            )
        )
    return out


def fetch_hn(session: requests.Session, since: datetime, min_points: int = MIN_HN_POINTS) -> list[Candidate]:
    resp = session.get(HN_FEED.format(points=min_points), timeout=TIMEOUT, headers={"User-Agent": USER_AGENT})
    resp.raise_for_status()
    return parse_hn_feed(resp.text, since)


def fetch_github_search(
    session: requests.Session, since: datetime, token: str, min_stars: int = MIN_GH_STARS
) -> list[Candidate]:
    query = f"created:>={since.date().isoformat()} stars:>={min_stars}"
    resp = session.get(
        GH_SEARCH,
        params={"q": query, "sort": "stars", "order": "desc", "per_page": 30},
        headers=_gh_headers(token),
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    return parse_github_search(resp.json(), since)


def fetch_releases(
    session: requests.Session, since: datetime, repos: list[str] = WATCHED_REPOS
) -> list[Candidate]:
    out: list[Candidate] = []
    for repo in repos:
        try:
            resp = session.get(
                f"https://github.com/{repo}/releases.atom",
                timeout=TIMEOUT,
                headers={"User-Agent": USER_AGENT},
            )
            resp.raise_for_status()
            out.extend(parse_releases_atom(resp.text, repo, since))
        except Exception as exc:  # noqa: BLE001 - một repo lỗi không được làm hỏng cả lần chạy
            log.warning("Không lấy được release của %s: %s", repo, exc)
    return out


def fetch_all(session: requests.Session, since: datetime, token: str) -> list[Candidate]:
    candidates: list[Candidate] = []
    sources = {
        "hn": lambda: fetch_hn(session, since),
        "github_search": lambda: fetch_github_search(session, since, token),
        "github_release": lambda: fetch_releases(session, since),
    }
    for name, fetch in sources.items():
        try:
            items = fetch()
            log.info("Nguồn %s: %d mục mới", name, len(items))
            candidates.extend(items)
        except Exception as exc:  # noqa: BLE001
            log.warning("Nguồn %s lỗi, bỏ qua: %s", name, exc)
    return candidates
