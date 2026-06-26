from __future__ import annotations

from ai_data_pipeline.cleaning import normalize_text
from ai_data_pipeline.dedupe import jaccard_similarity
from ai_data_pipeline.models import ProcessedSample
from ai_data_pipeline.scoring import classify_sample, score_sample


def test_normalize_text_removes_html_and_spaces() -> None:
    text = normalize_text("<p>数据&nbsp;清洗</p>\n\n很好！")
    assert text == "数据 清洗 很好!"


def test_jaccard_similarity_detects_similar_text() -> None:
    left = "如何学习 Python 数据清洗"
    right = "怎么学习 Python 数据清洗"
    assert jaccard_similarity(left, right) > 0.5


def test_score_sample_penalizes_spam() -> None:
    sample = ProcessedSample(
        id="x",
        source="test",
        question="如何领取资料",
        answer="免费领取资料，加微信 123456，点击链接马上领取。",
    )
    score, issues = score_sample(sample)
    assert score < 70
    assert "spam_or_marketing" in issues


def test_classify_sample_data_category() -> None:
    sample = ProcessedSample(
        id="x",
        source="test",
        question="如何做数据清洗和去重",
        answer="需要关注数据质量、字段标准化和重复样本过滤。",
    )
    assert classify_sample(sample) == "data"

