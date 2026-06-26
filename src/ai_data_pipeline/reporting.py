from __future__ import annotations

from collections import Counter
from datetime import datetime

from .models import ProcessedSample


def build_report(
    raw_count: int,
    clean_stats: dict[str, int],
    dedupe_stats: dict[str, int],
    samples: list[ProcessedSample],
    exported_count: int,
) -> str:
    category_counts = Counter(sample.category for sample in samples)
    quality_counts = Counter(sample.quality_level for sample in samples)
    issue_counts = Counter(issue for sample in samples for issue in sample.issues)

    lines = [
        "# 数据质量报告",
        "",
        f"- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 原始样本数: {raw_count}",
        f"- 清洗后样本数: {clean_stats.get('kept', 0)}",
        f"- 去重后样本数: {dedupe_stats.get('kept', 0)}",
        f"- 最终导出训练样本数: {exported_count}",
        "",
        "## 清洗过滤统计",
        "",
        "| 原因 | 数量 |",
        "| --- | ---: |",
    ]
    for key, value in clean_stats.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## 去重统计",
            "",
            "| 类型 | 数量 |",
            "| --- | ---: |",
        ]
    )
    for key, value in dedupe_stats.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## 质量等级分布",
            "",
            "| 等级 | 数量 |",
            "| --- | ---: |",
        ]
    )
    for key in ["high", "medium", "low"]:
        lines.append(f"| {key} | {quality_counts.get(key, 0)} |")

    lines.extend(
        [
            "",
            "## 类别分布",
            "",
            "| 类别 | 数量 |",
            "| --- | ---: |",
        ]
    )
    for key, value in sorted(category_counts.items()):
        lines.append(f"| {key} | {value} |")

    lines.extend(
        [
            "",
            "## 质量问题统计",
            "",
            "| 问题 | 数量 |",
            "| --- | ---: |",
        ]
    )
    if issue_counts:
        for key, value in sorted(issue_counts.items()):
            lines.append(f"| {key} | {value} |")
    else:
        lines.append("| none | 0 |")

    lines.extend(
        [
            "",
            "## 样本预览",
            "",
            "| ID | 类别 | 分数 | 等级 | 问题 |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for sample in samples[:8]:
        question = sample.question.replace("|", "/")[:40]
        lines.append(f"| {sample.id} | {sample.category} | {sample.quality_score} | {sample.quality_level} | {question} |")

    return "\n".join(lines) + "\n"


def build_streaming_report(
    raw_count: int,
    clean_stats: dict[str, int],
    dedupe_stats: dict[str, int],
    category_counts: Counter[str],
    quality_counts: Counter[str],
    issue_counts: Counter[str],
    preview_samples: list[ProcessedSample],
    exported_count: int,
) -> str:
    lines = [
        "# 数据质量报告",
        "",
        f"- 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- 原始样本数: {raw_count}",
        f"- 清洗后样本数: {clean_stats.get('kept', 0)}",
        f"- 去重后样本数: {dedupe_stats.get('kept', 0)}",
        f"- 最终导出训练样本数: {exported_count}",
        "",
        "## 清洗过滤统计",
        "",
        "| 原因 | 数量 |",
        "| --- | ---: |",
    ]
    for key, value in clean_stats.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## 去重统计", "", "| 类型 | 数量 |", "| --- | ---: |"])
    for key, value in dedupe_stats.items():
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## 质量等级分布", "", "| 等级 | 数量 |", "| --- | ---: |"])
    for key in ["high", "medium", "low"]:
        lines.append(f"| {key} | {quality_counts.get(key, 0)} |")

    lines.extend(["", "## 类别分布", "", "| 类别 | 数量 |", "| --- | ---: |"])
    for key, value in sorted(category_counts.items()):
        lines.append(f"| {key} | {value} |")

    lines.extend(["", "## 质量问题统计", "", "| 问题 | 数量 |", "| --- | ---: |"])
    if issue_counts:
        for key, value in sorted(issue_counts.items()):
            lines.append(f"| {key} | {value} |")
    else:
        lines.append("| none | 0 |")

    lines.extend(["", "## 样本预览", "", "| ID | 类别 | 分数 | 等级 | 问题 |", "| --- | --- | ---: | --- | --- |"])
    for sample in preview_samples:
        question = sample.question.replace("|", "/")[:40]
        lines.append(f"| {sample.id} | {sample.category} | {sample.quality_score} | {sample.quality_level} | {question} |")

    return "\n".join(lines) + "\n"
