from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RawSample:
    id: str
    source: str
    question: str
    answer: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedSample:
    id: str
    source: str
    question: str
    answer: str
    metadata: dict[str, Any] = field(default_factory=dict)
    category: str = "general"
    quality_score: int = 0
    quality_level: str = "low"
    issues: list[str] = field(default_factory=list)

    def to_instruction_record(self) -> dict[str, Any]:
        return {
            "instruction": self.question,
            "input": "",
            "output": self.answer,
            "category": self.category,
            "quality_score": self.quality_score,
            "quality_level": self.quality_level,
            "source": self.source,
            "metadata": self.metadata,
        }

