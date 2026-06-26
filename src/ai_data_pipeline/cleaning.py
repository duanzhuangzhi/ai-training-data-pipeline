from __future__ import annotations

import html
import re

from .models import ProcessedSample, RawSample

HTML_TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")

PUNCTUATION_MAP = str.maketrans(
    {
        "，": ",",
        "。": ".",
        "！": "!",
        "？": "?",
        "；": ";",
        "：": ":",
        "（": "(",
        "）": ")",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
    }
)


def normalize_text(text: str) -> str:
    text = html.unescape(text or "")
    text = HTML_TAG_RE.sub(" ", text)
    text = text.translate(PUNCTUATION_MAP)
    text = WHITESPACE_RE.sub(" ", text)
    return text.strip()


def clean_samples(samples: list[RawSample]) -> tuple[list[ProcessedSample], dict[str, int]]:
    cleaned: list[ProcessedSample] = []
    stats = {
        "empty_question": 0,
        "empty_answer": 0,
        "too_short_answer": 0,
        "kept": 0,
    }

    for sample in samples:
        question = normalize_text(sample.question)
        answer = normalize_text(sample.answer)
        if not question:
            stats["empty_question"] += 1
            continue
        if not answer:
            stats["empty_answer"] += 1
            continue
        if len(answer) < 12:
            stats["too_short_answer"] += 1
            continue
        cleaned.append(
            ProcessedSample(
                id=sample.id,
                source=sample.source,
                question=question,
                answer=answer,
                metadata=sample.metadata,
            )
        )
        stats["kept"] += 1

    return cleaned, stats


def clean_one(sample: RawSample) -> tuple[ProcessedSample | None, str | None]:
    question = normalize_text(sample.question)
    answer = normalize_text(sample.answer)
    if not question:
        return None, "empty_question"
    if not answer:
        return None, "empty_answer"
    if len(answer) < 12:
        return None, "too_short_answer"
    return (
        ProcessedSample(
            id=sample.id,
            source=sample.source,
            question=question,
            answer=answer,
            metadata=sample.metadata,
        ),
        None,
    )
