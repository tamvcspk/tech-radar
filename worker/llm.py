"""Lớp provider mỏng cho LLM. Đổi model hoặc nhà cung cấp chỉ cần thay class ở đây."""

from __future__ import annotations

from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProvider(Protocol):
    def generate_json(self, prompt: str, response_model: type[T]) -> T: ...


class GeminiProvider:
    """Gọi Gemini với structured output (JSON theo schema Pydantic)."""

    def __init__(self, api_key: str, model: str) -> None:
        from google import genai  # import muộn để unit test không cần SDK

        self._client = genai.Client(api_key=api_key)
        self._model = model

    def generate_json(self, prompt: str, response_model: type[T]) -> T:
        from google.genai import types

        response = self._client.models.generate_content(
            model=self._model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_model,
                temperature=0.2,
            ),
        )
        if not response.text:
            raise ValueError("Gemini trả về rỗng")
        return response_model.model_validate_json(response.text)
