from datetime import datetime, timezone

from worker import pipeline
from worker.llm import TransientLLMError
from worker.models import ArticleOutput, Candidate, GatekeeperOutput, Verdict

NOW = datetime(2026, 11, 24, 1, 0, tzinfo=timezone.utc)


def _candidate(title="Hello", url="https://example.com/a"):
    return Candidate(source="hn", title=title, url=url, description="desc", published=NOW)


class FakeLLM:
    def __init__(self, article_error=None):
        self.article_error = article_error

    def generate_json(self, prompt, response_model):
        if response_model is GatekeeperOutput:
            return GatekeeperOutput(verdicts=[Verdict(id=0, score=9, reason="r", topic="ai")])
        if self.article_error:
            raise self.article_error
        return ArticleOutput(summary="s", body_markdown="## Vấn đề\nx")


def _patch(monkeypatch, tmp_path, candidates):
    monkeypatch.setattr(pipeline, "STATE_PATH", tmp_path / "state.json")
    monkeypatch.setattr(pipeline, "OUT_DIR", tmp_path / "out")
    monkeypatch.setattr(pipeline, "fetch_all", lambda *a, **k: candidates)
    monkeypatch.setattr(pipeline, "fetch_material", lambda *a, **k: ("material", "fulltext"))
    real_write = pipeline.write_digest
    monkeypatch.setattr(pipeline, "write_digest", lambda d, a: real_write(d, a, docs_dir=tmp_path / "docs"))


def _settings():
    from worker.config import Settings

    return Settings("", "m", "", "", True, "", "https://x")


def test_stale_manifest_is_removed_when_nothing_new(monkeypatch, tmp_path):
    _patch(monkeypatch, tmp_path, [])
    manifest = tmp_path / "out" / pipeline.TELEGRAM_MANIFEST
    manifest.parent.mkdir()
    manifest.write_text("{}", encoding="utf-8")
    assert pipeline.run_generate(_settings(), FakeLLM(), None, now=NOW) is None
    assert not manifest.exists()


def test_transient_llm_error_does_not_mark_item_failed(monkeypatch, tmp_path):
    import json

    _patch(monkeypatch, tmp_path, [_candidate()])
    result = pipeline.run_generate(_settings(), FakeLLM(TransientLLMError("429")), None, now=NOW)
    assert result is None
    state = json.loads((tmp_path / "state.json").read_text(encoding="utf-8"))
    assert state["items"] == {}  # lần chạy sau còn thử lại được


def test_success_writes_digest_and_manifest(monkeypatch, tmp_path):
    _patch(monkeypatch, tmp_path, [_candidate()])
    digest = pipeline.run_generate(_settings(), FakeLLM(), None, now=NOW)
    assert digest is not None and (digest / "index.md").exists()
    assert (tmp_path / "out" / pipeline.TELEGRAM_MANIFEST).exists()
