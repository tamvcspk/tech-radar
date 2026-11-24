from datetime import datetime, timezone

from worker.article import write_article
from worker.gatekeeper import select, score_candidates
from worker.models import ArticleOutput, Candidate, GatekeeperOutput, Scored, Verdict

NOW = datetime(2026, 11, 24, tzinfo=timezone.utc)


class FakeLLM:
    """Không gọi API thật. Trả về output đã định sẵn theo loại schema."""

    def __init__(self, responses):
        self.responses = responses
        self.prompts = []

    def generate_json(self, prompt, response_model):
        self.prompts.append(prompt)
        return self.responses[response_model]


def cands(n):
    return [
        Candidate(source="hn", title=f"Item {i}", url=f"https://example.com/{i}", published=NOW)
        for i in range(n)
    ]


def v(id_, score, topic="ai"):
    return Verdict(id=id_, score=score, reason="lý do", topic=topic)


def test_score_maps_verdicts_by_id_and_clamps_scores():
    items = cands(3)
    llm = FakeLLM({GatekeeperOutput: GatekeeperOutput(verdicts=[v(0, 42), v(2, -3)])})
    scored = score_candidates(items, llm)
    assert [s.candidate.title for s in scored] == ["Item 0", "Item 2"]
    assert scored[0].verdict.score == 10
    assert scored[1].verdict.score == 1


def test_score_ignores_unknown_ids_and_empty_input():
    llm = FakeLLM({GatekeeperOutput: GatekeeperOutput(verdicts=[v(99, 9)])})
    assert score_candidates(cands(2), llm) == []
    assert score_candidates([], llm) == []


def test_select_applies_threshold_and_topic_cap():
    items = cands(5)
    scored = [
        Scored(candidate=items[0], verdict=v(0, 9, "ai")),
        Scored(candidate=items[1], verdict=v(1, 8, "ai")),
        Scored(candidate=items[2], verdict=v(2, 8, "ai")),  # vượt trần 2 mục AI
        Scored(candidate=items[3], verdict=v(3, 7, "infra")),
        Scored(candidate=items[4], verdict=v(4, 6, "web")),  # dưới ngưỡng
    ]
    chosen = select(scored)
    assert [s.candidate.title for s in chosen] == ["Item 0", "Item 1", "Item 3"]


def test_select_can_return_nothing():
    items = cands(2)
    scored = [Scored(candidate=i, verdict=v(n, 5)) for n, i in enumerate(items)]
    assert select(scored) == []


def test_write_article_passes_quality_into_prompt_and_builds_slug():
    item = cands(1)[0]
    llm = FakeLLM({ArticleOutput: ArticleOutput(summary="Dòng 1\nDòng 2", body_markdown="## Vấn đề\nChưa rõ.")})
    article = write_article(item, v(0, 8), "nội dung", "description", llm)
    assert "chỉ có mô tả ngắn" in llm.prompts[0]
    assert article.summary == "Dòng 1\nDòng 2"
    assert article.slug.startswith("item-0-")
