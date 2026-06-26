from __future__ import annotations

import re

from .models import ProcessedSample

SPAM_WORDS = ["加微信", "限时优惠", "点击链接", "免费领取", "马上领取", "私信"]
TECH_KEYWORDS = ["python", "脚本", "爬虫", "工程", "日志", "自动化", "pipeline"]
DATA_KEYWORDS = ["数据", "清洗", "去重", "质量", "筛选", "数据集", "字段"]
AI_KEYWORDS = ["ai", "模型", "训练", "微调", "分类", "向量", "instruction"]
CAREER_KEYWORDS = ["简历", "面试", "岗位", "实习", "投递", "项目截图"]


def enrich_samples(samples: list[ProcessedSample]) -> list[ProcessedSample]:
    enriched: list[ProcessedSample] = []
    for sample in samples:
        score, issues = score_sample(sample)
        sample.quality_score = score
        sample.quality_level = quality_level(score)
        sample.issues = issues
        sample.category = classify_sample(sample)
        enriched.append(sample)
    return enriched


def score_sample(sample: ProcessedSample) -> tuple[int, list[str]]:
    text = sample.question + " " + sample.answer
    score = 100
    issues: list[str] = []

    if len(sample.question) < 6:
        score -= 10
        issues.append("question_too_short")
    if len(sample.answer) < 30:
        score -= 18
        issues.append("answer_too_short")
    if len(sample.answer) > 350:
        score -= 8
        issues.append("answer_too_long")
    if any(word in text for word in SPAM_WORDS):
        score -= 45
        issues.append("spam_or_marketing")
    if abnormal_char_ratio(text) > 0.08:
        score -= 18
        issues.append("high_abnormal_char_ratio")
    if token_overlap(sample.question, sample.answer) == 0:
        score -= 10
        issues.append("weak_question_answer_overlap")

    score = max(0, min(100, score))
    return score, issues


def quality_level(score: int) -> str:
    if score >= 80:
        return "high"
    if score >= 60:
        return "medium"
    return "low"


def classify_sample(sample: ProcessedSample) -> str:
    text = (sample.question + " " + sample.answer).lower()
    scores = {
        "tech": keyword_count(text, TECH_KEYWORDS),
        "data": keyword_count(text, DATA_KEYWORDS),
        "ai": keyword_count(text, AI_KEYWORDS),
        "career": keyword_count(text, CAREER_KEYWORDS),
    }
    best_category = max(scores, key=scores.get)
    return best_category if scores[best_category] > 0 else "general"


def keyword_count(text: str, keywords: list[str]) -> int:
    return sum(1 for keyword in keywords if keyword.lower() in text)


def abnormal_char_ratio(text: str) -> float:
    if not text:
        return 0.0
    abnormal = re.findall(r"[^\w\s\u4e00-\u9fff,.!?;:'\"()/-]", text)
    return len(abnormal) / len(text)


def token_overlap(question: str, answer: str) -> float:
    q_tokens = meaningful_tokens(question)
    a_tokens = meaningful_tokens(answer)
    if not q_tokens or not a_tokens:
        return 0.0
    return len(q_tokens & a_tokens) / len(q_tokens | a_tokens)


def meaningful_tokens(text: str) -> set[str]:
    ascii_tokens = set(re.findall(r"[a-zA-Z][a-zA-Z0-9_-]+", text.lower()))
    chinese_phrases = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    chinese_bigrams: set[str] = set()
    for phrase in chinese_phrases:
        chinese_bigrams.update(phrase[index : index + 2] for index in range(len(phrase) - 1))
    return ascii_tokens | chinese_bigrams
