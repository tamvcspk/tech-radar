"""Kiểu dữ liệu dùng xuyên suốt pipeline."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Source = Literal["hn", "github_search", "github_release"]
Quality = Literal["fulltext", "readme", "description"]


class Candidate(BaseModel):
    """Một mục thô từ nguồn, chưa qua chấm điểm."""

    source: Source
    title: str
    url: str
    description: str = ""
    published: datetime
    points: int | None = None
    repo: str | None = None  # "owner/name" khi mục là repo GitHub gốc


class Verdict(BaseModel):
    """Kết quả chấm điểm của Gatekeeper cho một mục."""

    id: int = Field(description="Mã số của mục trong danh sách đầu vào")
    score: int = Field(description="Điểm từ 1 đến 10")
    reason: str = Field(description="Lý do chấm điểm, một câu ngắn")
    topic: str = Field(description="Chủ đề ngắn, ví dụ: AI, Infra, Database, Frontend, Security")


class GatekeeperOutput(BaseModel):
    verdicts: list[Verdict]


class ArticleOutput(BaseModel):
    """Nội dung LLM sinh ra ở chặng 2."""

    summary: str = Field(description="Tóm tắt 2 dòng tiếng Việt, văn bản thuần, không HTML, không Markdown")
    body_markdown: str = Field(
        description=(
            "Nội dung Markdown tiếng Việt gồm đúng 4 mục bắt đầu bằng '## ': "
            "Vấn đề; Cách hoạt động; Trade-off và hạn chế; Điểm đáng chú ý. Không dùng tiêu đề '#'."
        )
    )


class Scored(BaseModel):
    candidate: Candidate
    verdict: Verdict


class Article(BaseModel):
    candidate: Candidate
    verdict: Verdict
    slug: str
    summary: str
    body_markdown: str
    quality: Quality
