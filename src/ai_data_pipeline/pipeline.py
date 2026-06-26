from __future__ import annotations

from collections import Counter
import json
import logging
from pathlib import Path

from .cleaning import clean_one
from .dedupe import StreamingDeduper
from .io_utils import write_markdown
from .loaders import iter_raw_samples
from .models import ProcessedSample
from .reporting import build_streaming_report
from .scoring import score_sample, quality_level, classify_sample

LOGGER = logging.getLogger(__name__)


def run_pipeline(project_root: Path, min_export_score: int = 60) -> dict[str, Path | int]:
    data_dir = project_root / "data"
    raw_dir = data_dir / "raw"
    processed_dir = data_dir / "processed"
    export_dir = data_dir / "exports"
    report_dir = project_root / "reports"

    processed_dir.mkdir(parents=True, exist_ok=True)
    export_dir.mkdir(parents=True, exist_ok=True)

    raw_count = 0
    exported_count = 0
    clean_stats = {"empty_question": 0, "empty_answer": 0, "too_short_answer": 0, "kept": 0}
    category_counts: Counter[str] = Counter()
    quality_counts: Counter[str] = Counter()
    issue_counts: Counter[str] = Counter()
    preview_samples: list[ProcessedSample] = []
    deduper = StreamingDeduper()

    cleaned_path = processed_dir / "cleaned_samples.jsonl"
    scored_path = processed_dir / "scored_samples.jsonl"
    export_path = export_dir / "instruction_dataset.jsonl"

    LOGGER.info("Streaming raw samples from %s", raw_dir)
    with cleaned_path.open("w", encoding="utf-8") as cleaned_file, scored_path.open("w", encoding="utf-8") as scored_file, export_path.open("w", encoding="utf-8") as export_file:
        for raw_sample in iter_raw_samples(raw_dir):
            raw_count += 1
            cleaned_sample, reject_reason = clean_one(raw_sample)
            if reject_reason:
                clean_stats[reject_reason] += 1
                continue

            assert cleaned_sample is not None
            clean_stats["kept"] += 1
            cleaned_file.write(json.dumps(_sample_record(cleaned_sample), ensure_ascii=False) + "\n")

            if not deduper.accept(cleaned_sample):
                continue

            score, issues = score_sample(cleaned_sample)
            cleaned_sample.quality_score = score
            cleaned_sample.quality_level = quality_level(score)
            cleaned_sample.issues = issues
            cleaned_sample.category = classify_sample(cleaned_sample)

            category_counts[cleaned_sample.category] += 1
            quality_counts[cleaned_sample.quality_level] += 1
            issue_counts.update(cleaned_sample.issues)
            if len(preview_samples) < 8:
                preview_samples.append(cleaned_sample)

            scored_file.write(json.dumps(_sample_record(cleaned_sample), ensure_ascii=False) + "\n")
            if cleaned_sample.quality_score >= min_export_score:
                export_file.write(json.dumps(cleaned_sample.to_instruction_record(), ensure_ascii=False) + "\n")
                exported_count += 1

            if raw_count % 100000 == 0:
                LOGGER.info("Processed %s raw samples, exported %s", raw_count, exported_count)

    LOGGER.info("Loaded raw samples: %s", raw_count)
    LOGGER.info("Cleaned samples: %s", clean_stats["kept"])
    LOGGER.info("Deduped samples: %s", deduper.stats["kept"])
    LOGGER.info("Exported samples: %s", exported_count)

    report = build_streaming_report(
        raw_count=raw_count,
        clean_stats=clean_stats,
        dedupe_stats=deduper.stats,
        category_counts=category_counts,
        quality_counts=quality_counts,
        issue_counts=issue_counts,
        preview_samples=preview_samples,
        exported_count=exported_count,
    )
    report_path = report_dir / "data_quality_report.md"
    write_markdown(report_path, report)
    LOGGER.info("Report written to %s", report_path)

    return {
        "raw_count": raw_count,
        "cleaned_count": clean_stats["kept"],
        "deduped_count": deduper.stats["kept"],
        "exported_count": exported_count,
        "report_path": report_path,
        "export_path": export_path,
    }


def _sample_record(sample: ProcessedSample) -> dict[str, object]:
    return {
        "id": sample.id,
        "source": sample.source,
        "question": sample.question,
        "answer": sample.answer,
        "metadata": sample.metadata,
        "category": sample.category,
        "quality_score": sample.quality_score,
        "quality_level": sample.quality_level,
        "issues": sample.issues,
    }
