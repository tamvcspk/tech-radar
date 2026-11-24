from datetime import datetime, timezone

from worker import enrich
from worker.models import Candidate

NOW = datetime(2026, 11, 24, tzinfo=timezone.utc)


class FakeResp:
    def __init__(self, status_code=200, json_data=None, text=""):
        self.status_code = status_code
        self._json = json_data
        self.text = text

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._json


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)

    def get(self, url, **kwargs):
        return self.responses.pop(0)


def _cand(url="https://example.com/post", repo=None, description="mô tả ngắn"):
    return Candidate(source="hn", title="T", url=url, description=description, published=NOW, repo=repo)


def test_fetch_material_reads_github_readme_when_license_is_clear():
    session = FakeSession([
        FakeResp(200, json_data={"license": {"spdx_id": "MIT"}}),
        FakeResp(200, text="# Project README"),
    ])
    text, quality = enrich.fetch_material(_cand(url="https://github.com/a/b", repo="a/b"), session, "")
    assert text == "# Project README"
    assert quality == "readme"


def test_fetch_material_skips_readme_for_noassertion_license():
    session = FakeSession([FakeResp(200, json_data={"license": {"spdx_id": "NOASSERTION"}})])
    text, quality = enrich.fetch_material(_cand(url="https://github.com/a/b", repo="a/b"), session, "")
    assert text == "mô tả ngắn"
    assert quality == "description"


def test_fetch_material_falls_back_to_description_when_readme_is_404():
    session = FakeSession([
        FakeResp(200, json_data={"license": {"spdx_id": "Apache-2.0"}}),
        FakeResp(404),
    ])
    text, quality = enrich.fetch_material(_cand(url="https://github.com/a/b", repo="a/b"), session, "")
    assert text == "mô tả ngắn"
    assert quality == "description"


def test_fetch_material_uses_web_text_and_falls_back_on_error(monkeypatch):
    monkeypatch.setattr(enrich, "_web_text", lambda url: "full article body")
    text, quality = enrich.fetch_material(_cand(), FakeSession([]), "")
    assert text == "full article body"
    assert quality == "fulltext"

    def boom(url):
        raise RuntimeError("network")

    monkeypatch.setattr(enrich, "_web_text", boom)
    text, quality = enrich.fetch_material(_cand(), FakeSession([]), "")
    assert text == "mô tả ngắn"
    assert quality == "description"

