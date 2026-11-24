"""Lớp provider mỏng cho LLM. Đổi model hoặc nhà cung cấp chỉ cần thay class ở đây."""

from __future__ import annotations

import logging
import time
from typing import Callable, Protocol, TypeVar

from pydantic import BaseModel

log = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")

RETRY_CODES = {429, 500, 502, 503, 504}
MAX_ATTEMPTS = 4
BASE_DELAY = 5.0  # giây; gấp đôi sau mỗi lần thử (5, 10, 20)


class TransientLLMError(RuntimeError):
    """Lỗi tạm thời (rate limit, server quá tải) vẫn còn sau khi đã thử lại."""


class LLMProvider(Protocol):
    def generate_json(self, prompt: str, response_model: type[T]) -> T: ...


def is_transient(exc: Exception) -> bool:
    return getattr(exc, "code", None) in RETRY_CODES


def call_with_retry(
    fn: Callable[[], R],
    attempts: int = MAX_ATTEMPTS,
    base_delay: float = BASE_DELAY,
    sleep: Callable[[float], None] = time.sleep,
) -> R:
    """Gọi fn, thử lại với exponential backoff khi gặp lỗi tạm thời (429/5xx)."""
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            if not is_transient(exc):
                raise
            if attempt == attempts:
                raise TransientLLMError(str(exc)) from exc
            delay = base_delay * 2 ** (attempt - 1)
            log.warning("LLM lỗi tạm thời (%s), thử lại sau %.0fs (lần %d/%d)", exc, delay, attempt, attempts)
            sleep(delay)
    raise AssertionError("không tới được")  # pragma: no cover


class GeminiProvider:
    """Gọi Gemini với structured output (JSON theo schema Pydantic)."""

    def __init__(self, api_key: str, model: str) -> None:
        from google import genai  # import muộn để unit test không cần SDK

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate_json(self, prompt: str, response_model: type[T]) -> T:
        from google.genai import types

        response = call_with_retry(
            lambda: self._client.models.generate_content(
                model=self._model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=response_model,
                    temperature=0.2,
                ),
            )
        )
        if not response.text:
            raise ValueError("Gemini trả về rỗng")
        return response_model.model_validate_json(response.text)
