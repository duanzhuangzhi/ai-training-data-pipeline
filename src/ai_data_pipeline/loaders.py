from __future__ import annotations

import re
from pathlib import Path

from .io_utils import iter_csv, iter_jsonl
from .models import RawSample


def load_raw_samples(raw_dir: Path) -> list[RawSample]:
    return list(iter_raw_samples(raw_dir))


def iter_raw_samples(raw_dir: Path):
    for path in sorted(raw_dir.iterdir()):
        if path.suffix.lower() == ".jsonl":
            yield from _iter_jsonl(path)
        elif path.suffix.lower() == ".csv":
            yield from _iter_csv(path)
        elif path.suffix.lower() == ".txt":
            yield from _load_txt(path)


def _load_jsonl(path: Path) -> list[RawSample]:
    return list(_iter_jsonl(path))


def _iter_jsonl(path: Path):
    for index, record in enumerate(iter_jsonl(path), start=1):
        yield RawSample(
            id=str(record.get("id") or f"{path.stem}-{index:04d}"),
            source=str(record.get("source") or path.stem),
            question=str(record.get("question") or ""),
            answer=str(record.get("answer") or ""),
            metadata=dict(record.get("metadata") or {}),
        )


def _load_csv(path: Path) -> list[RawSample]:
    return list(_iter_csv(path))


def _iter_csv(path: Path):
    for index, record in enumerate(iter_csv(path), start=1):
        metadata = {k: v for k, v in record.items() if k not in {"id", "source", "question", "answer"}}
        yield RawSample(
            id=str(record.get("id") or f"{path.stem}-{index:04d}"),
            source=str(record.get("source") or path.stem),
            question=str(record.get("question") or ""),
            answer=str(record.get("answer") or ""),
            metadata=metadata,
        )


def _load_txt(path: Path) -> list[RawSample]:
    text = path.read_text(encoding="utf-8")
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text) if block.strip()]
    samples: list[RawSample] = []
    for index, block in enumerate(blocks, start=1):
        question_match = re.search(r"问题[:：]\s*(.+)", block)
        answer_match = re.search(r"答案[:：]\s*(.+)", block)
        samples.append(
            RawSample(
                id=f"{path.stem}-{index:04d}",
                source=path.stem,
                question=question_match.group(1).strip() if question_match else "",
                answer=answer_match.group(1).strip() if answer_match else "",
                metadata={"raw_block": block},
            )
        )
    return samples
