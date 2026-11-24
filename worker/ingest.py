"""Lấy mục mới từ 3 nguồn: hnrss (HN), GitHub Search API, GitHub Releases .atom.

Mỗi nguồn lỗi thì chỉ bỏ nguồn đó, không làm hỏng cả lần chạy.
"""

from __future__ import annotations

import html
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

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


# Các đường dẫn 2 đoạn của github.com không phải repo.
NON_REPO_OWNERS = {
    "orgs", "topics", "sponsors", "features", "settings", "marketplace", "collections",
    "apps", "enterprise", "about", "pricing", "explore", "trending", "readme", "users",
}
# Phần boilerplate hnrss gắn vào mô tả, không mang thông tin về nội dung bài.
HN_BOILERPLATE = re.compile(
    r"Article URL:\s*\S+|Comments URL:\s*\S+|Points:\s*\d+|#\s*Comments:\s*\d+", re.IGNORECASE
)
# Tag của bản canary/nightly/alpha/beta/rc (kể cả dạng CPython v3.14.0a7, Go go1.24rc1).
PRERELEASE_TAG = re.compile(
    r"canary|nightly|snapshot"
    r"|(?:^|[-_.]|\d)(?:alpha|beta|rc|dev|pre)(?:[-_.]?\d+)?(?:$|[-_.])"
    r"|\d[ab]\d+(?:$|[-_.])",
    re.IGNORECASE,
)


def github_repo_from_url(url: str) -> str | None:
    """'owner/name' nếu url là trang gốc của một repo GitHub, ngược lại None."""
    parts = urlsplit(url.strip())
    if parts.scheme.lower() not in {"http", "https"}:
        return None
    if parts.netloc.lower().removeprefix("www.") != "github.com":
        return None
    segments = [s for s in parts.path.split("/") if s]
    if len(segments) != 2:
        return None
    owner = segments[0]
    name = re.sub(r"\.git$", "", segments[1], flags=re.IGNORECASE)
    if not owner or not name or owner.lower() in NON_REPO_OWNERS:
        return None
    return f"{owner}/{name}"


def _plain_text(markup: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", markup)).split())


def parse_hn_feed(xml_text: str, since: datetime) -> list[Candidate]:
    root = ET.fromstring(xml_text)
    out: list[Candidate] = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = item.findtext("pubDate")
        if not title or not link or not pub:
            continue
        try:
            published = parsedate_to_datetime(pub)
        except (TypeError, ValueError):
            continue
        if published.tzinfo is None:  # feed thiếu timezone: coi là UTC để so sánh được
            published = published.replace(tzinfo=timezone.utc)
        if published < since:
            continue
        desc_html = item.findtext("description") or ""
        match = re.search(r"Points:\s*(\d+)", desc_html)
        text = " ".join(HN_BOILERPLATE.sub(" ", _plain_text(desc_html)).split())
        out.append(
            Candidate(
                source="hn",
                title=title,
                url=link,
                description=text[:500],
                published=published,
                points=int(match.group(1)) if match else None,
                repo=github_repo_from_url(link),
            )
        )
    return out


# Repo cheat/crack/bot ví/lừa đảo hay xuất hiện trong kết quả tìm kiếm theo sao. Loại từ đầu.
# Các từ chung chung (hack, cheat, crack...) phải đứng độc lập để không chặn nhầm hackathon, cheatsheet...
SUSPICIOUS = re.compile(
    r"(?<![a-z0-9])(?:cheats?|cheating|hacks?|hacking|cracks?|cracked|cracking|spoof\w*"
    r"|exploits?|activators?|unlockers?)(?![a-z0-9])"
    r"|keygen|aimbot|wallhack|roblox|fortnite|valorant|fisch|blox|rob-?run|recoil|pirate|sniper"
    r"|pump-?fun|mnemonic|arbitrage|market-?maker|volume-?bump|trial-?reset|gta-?6|hwid|license-?key",
    re.IGNORECASE,
)


def is_suspicious_repo(full_name: str, description: str) -> bool:
    return bool(SUSPICIOUS.search(f"{full_name} {description}"))


def parse_github_search(payload: dict, since: datetime) -> list[Candidate]:
    out: list[Candidate] = []
    for item in payload.get("items", []):
        published = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
        if published < since:
            continue
        spdx = ((item.get("license") or {}).get("spdx_id") or "").strip()
        if item.get("fork") or item.get("archived") or not spdx or spdx == "NOASSERTION":
            continue
        if is_suspicious_repo(item["full_name"], item.get("description") or ""):
            log.info("Bỏ repo đáng ngờ: %s", item["full_name"])
            continue
        desc = (item.get("description") or "")[:500]
        log.info(
            "GitHub repo: %s (stars=%s, forks=%s, lang=%s, desc_len=%d)",
            item["full_name"],
            item.get("stargazers_count"),
            item.get("forks_count"),
            item.get("language"),
            len(desc),
        )
        out.append(
            Candidate(
                source="github_search",
                title=item["full_name"],
                url=item["html_url"],
                description=desc,
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
        href = (link_el.get("href") or "").strip()
        if not href or PRERELEASE_TAG.search(href.rsplit("/", 1)[-1]):
            continue
        published = datetime.fromisoformat(updated.replace("Z", "+00:00"))
        if published < since:
            continue
        out.append(
            Candidate(
                source="github_release",
                title=f"{repo} {title}",
                url=href,
                description=_plain_text(entry.findtext(f"{ATOM}content") or "")[:500],
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
