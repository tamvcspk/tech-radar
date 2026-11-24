import os

import pytest
import requests

from worker import telegram
from worker.config import Settings, load_dotenv
from worker.llm import TransientLLMError, call_with_retry


class FakeApiError(Exception):
    def __init__(self, code: int):
        super().__init__(f"error {code}")
        self.code = code


def test_retry_recovers_after_transient_errors_with_backoff():
    calls, sleeps = [], []

    def fn():
        calls.append(1)
        if len(calls) < 3:
            raise FakeApiError(429)
        return "ok"

    assert call_with_retry(fn, base_delay=1, sleep=sleeps.append) == "ok"
    assert sleeps == [1, 2]


def test_retry_gives_up_with_transient_error():
    def fn():
        raise FakeApiError(503)

    with pytest.raises(TransientLLMError):
        call_with_retry(fn, attempts=2, sleep=lambda _: None)


def test_retry_does_not_swallow_permanent_errors():
    calls = []

    def fn():
        calls.append(1)
        raise FakeApiError(400)

    with pytest.raises(FakeApiError):
        call_with_retry(fn, sleep=lambda _: None)
    assert len(calls) == 1


def test_load_dotenv_handles_quotes_comments_and_export(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text(
        'T_QUOTED="AIza abc"  # ghi chú\nT_SINGLE=\'x y\'\nT_PLAIN=value # comment\nexport T_EXPORT=1\n# T_SKIP=1\n',
        encoding="utf-8",
    )
    for name in ("T_QUOTED", "T_SINGLE", "T_PLAIN", "T_EXPORT"):
        monkeypatch.delenv(name, raising=False)
    load_dotenv(env)
    try:
        assert os.environ["T_QUOTED"] == "AIza abc"
        assert os.environ["T_SINGLE"] == "x y"
        assert os.environ["T_PLAIN"] == "value"
        assert os.environ["T_EXPORT"] == "1"
    finally:
        for name in ("T_QUOTED", "T_SINGLE", "T_PLAIN", "T_EXPORT"):
            os.environ.pop(name, None)


def _settings() -> Settings:
    return Settings(
        gemini_api_key="", gemini_model="m", telegram_bot_token="SECRET-TOKEN",
        telegram_chat_id="1", dry_run=False, github_token="", site_base_url="https://x",
    )


def test_send_message_error_has_telegram_description_but_no_token(monkeypatch):
    class Resp:
        ok = False
        status_code = 400
        text = '{"ok":false,"description":"Bad Request: chat not found"}'

    monkeypatch.setattr(telegram.requests, "post", lambda *a, **k: Resp())
    with pytest.raises(RuntimeError) as err:
        telegram.send_message(_settings(), "hi", dry_run=False)
    assert "chat not found" in str(err.value)
    assert "SECRET-TOKEN" not in str(err.value)


def test_send_message_network_error_hides_token(monkeypatch):
    def boom(url, **kwargs):
        raise requests.ConnectionError(f"failed to reach {url}")

    monkeypatch.setattr(telegram.requests, "post", boom)
    with pytest.raises(RuntimeError) as err:
        telegram.send_message(_settings(), "hi", dry_run=False)
    assert "SECRET-TOKEN" not in str(err.value)
    assert err.value.__cause__ is None
