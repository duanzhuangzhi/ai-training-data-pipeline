from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    scored_path = project_root / "data" / "processed" / "scored_samples.jsonl"
    export_path = project_root / "data" / "exports" / "instruction_dataset.jsonl"
    report_path = project_root / "reports" / "data_quality_report.md"
    dashboard_path = project_root / "reports" / "dashboard.html"

    if not scored_path.exists():
        raise SystemExit("Missing scored_samples.jsonl. Run scripts/run_pipeline.py first.")

    report_metrics = parse_report_metrics(report_path)
    stats = summarize_scored_samples(scored_path)
    exported_count = count_lines(export_path) if export_path.exists() else 0

    html = render_dashboard(
        report_metrics=report_metrics,
        scored_stats=stats,
        exported_count=exported_count,
    )
    dashboard_path.write_text(html, encoding="utf-8")
    print(f"Dashboard written to: {dashboard_path}")


def parse_report_metrics(path: Path) -> dict[str, int]:
    metrics: dict[str, int] = {}
    if not path.exists():
        return metrics

    labels = {
        "原始样本数": "raw_count",
        "清洗后样本数": "cleaned_count",
        "去重后样本数": "deduped_count",
        "最终导出训练样本数": "exported_count",
    }
    for line in path.read_text(encoding="utf-8").splitlines():
        for label, key in labels.items():
            if line.startswith(f"- {label}:"):
                metrics[key] = int(line.split(":", 1)[1].strip())
    return metrics


def summarize_scored_samples(path: Path) -> dict[str, object]:
    total = 0
    category_counts: Counter[str] = Counter()
    quality_counts: Counter[str] = Counter()
    issue_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()
    score_buckets: Counter[str] = Counter()
    preview: list[dict[str, object]] = []
    low_quality_preview: list[dict[str, object]] = []

    with path.open("r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue
            total += 1
            record = json.loads(line)
            category_counts[str(record.get("category", "unknown"))] += 1
            quality_counts[str(record.get("quality_level", "unknown"))] += 1
            source_counts[str(record.get("source", "unknown"))] += 1
            score = int(record.get("quality_score", 0))
            score_buckets[bucket_score(score)] += 1
            issue_counts.update(str(issue) for issue in record.get("issues", []))

            if len(preview) < 8:
                preview.append(record)
            if score < 60 and len(low_quality_preview) < 8:
                low_quality_preview.append(record)

    return {
        "total": total,
        "category_counts": category_counts,
        "quality_counts": quality_counts,
        "issue_counts": issue_counts,
        "source_counts": source_counts,
        "score_buckets": score_buckets,
        "preview": preview,
        "low_quality_preview": low_quality_preview,
    }


def count_lines(path: Path) -> int:
    count = 0
    with path.open("r", encoding="utf-8") as file:
        for _ in file:
            count += 1
    return count


def bucket_score(score: int) -> str:
    if score >= 90:
        return "90-100"
    if score >= 80:
        return "80-89"
    if score >= 70:
        return "70-79"
    if score >= 60:
        return "60-69"
    return "0-59"


def render_dashboard(
    report_metrics: dict[str, int],
    scored_stats: dict[str, object],
    exported_count: int,
) -> str:
    raw_count = report_metrics.get("raw_count", 0)
    cleaned_count = report_metrics.get("cleaned_count", 0)
    deduped_count = report_metrics.get("deduped_count", int(scored_stats["total"]))
    final_exported = report_metrics.get("exported_count", exported_count)

    category_counts = scored_stats["category_counts"]
    quality_counts = scored_stats["quality_counts"]
    issue_counts = scored_stats["issue_counts"]
    source_counts = scored_stats["source_counts"]
    score_buckets = scored_stats["score_buckets"]
    preview = scored_stats["preview"]
    low_quality_preview = scored_stats["low_quality_preview"]

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI Training Data Pipeline Dashboard</title>
  <style>
    :root {{
      --bg: #f7f8fa;
      --panel: #ffffff;
      --text: #1f2937;
      --muted: #667085;
      --line: #d9dee7;
      --blue: #2563eb;
      --green: #0f9f6e;
      --amber: #b7791f;
      --red: #c2410c;
      --ink: #111827;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Segoe UI", Arial, "Microsoft YaHei", sans-serif;
    }}
    header {{
      padding: 28px 36px 18px;
      border-bottom: 1px solid var(--line);
      background: #fff;
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 28px;
      letter-spacing: 0;
    }}
    .subtitle {{ margin: 0; color: var(--muted); font-size: 14px; }}
    main {{ padding: 24px 36px 40px; max-width: 1440px; margin: 0 auto; }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }}
    .metric, .panel {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .metric {{ padding: 16px; }}
    .metric .label {{ color: var(--muted); font-size: 13px; }}
    .metric .value {{ margin-top: 8px; font-size: 30px; font-weight: 700; color: var(--ink); }}
    .metric .note {{ margin-top: 8px; color: var(--muted); font-size: 12px; }}
    .layout {{
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
    }}
    .panel {{ padding: 18px; }}
    .panel h2 {{ margin: 0 0 14px; font-size: 18px; }}
    .bar-row {{ display: grid; grid-template-columns: 120px 1fr 96px; gap: 10px; align-items: center; margin: 10px 0; }}
    .bar-label {{ color: var(--muted); font-size: 13px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .bar-track {{ height: 12px; background: #eef2f7; border-radius: 999px; overflow: hidden; }}
    .bar-fill {{ height: 100%; background: var(--blue); border-radius: 999px; }}
    .bar-value {{ text-align: right; font-variant-numeric: tabular-nums; font-size: 13px; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ border-top: 1px solid var(--line); padding: 10px 8px; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 600; }}
    .score {{ font-weight: 700; }}
    .tag {{ display: inline-block; padding: 2px 8px; border: 1px solid var(--line); border-radius: 999px; color: var(--muted); background: #fafafa; }}
    .wide {{ grid-column: 1 / -1; }}
    @media (max-width: 900px) {{
      header, main {{ padding-left: 18px; padding-right: 18px; }}
      .grid, .layout {{ grid-template-columns: 1fr; }}
      .bar-row {{ grid-template-columns: 96px 1fr 80px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>AI 训练数据 Pipeline Dashboard</h1>
    <p class="subtitle">生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} · 百万级中文问答数据清洗、去重、评分、分类与导出</p>
  </header>
  <main>
    <section class="grid">
      {metric_card("原始样本", raw_count, "生成/导入的问答样本总量")}
      {metric_card("清洗后", cleaned_count, f"过滤 {raw_count - cleaned_count:,} 条无效样本")}
      {metric_card("去重后", deduped_count, f"去除 {cleaned_count - deduped_count:,} 条重复/近似重复")}
      {metric_card("最终导出", final_exported, "可用于 instruction 微调格式")}
    </section>

    <section class="layout">
      <div class="panel">
        <h2>处理漏斗</h2>
        {bar_chart([
            ("Raw", raw_count),
            ("Cleaned", cleaned_count),
            ("Deduped", deduped_count),
            ("Exported", final_exported),
        ])}
      </div>
      <div class="panel">
        <h2>质量等级</h2>
        {bar_chart(counter_items(quality_counts, ["high", "medium", "low"]))}
      </div>
    </section>

    <section class="layout">
      <div class="panel">
        <h2>主题类别分布</h2>
        {bar_chart(counter_items(category_counts))}
      </div>
      <div class="panel">
        <h2>质量分区间</h2>
        {bar_chart(counter_items(score_buckets, ["90-100", "80-89", "70-79", "60-69", "0-59"]))}
      </div>
    </section>

    <section class="layout">
      <div class="panel">
        <h2>质量问题统计</h2>
        {bar_chart(counter_items(issue_counts))}
      </div>
      <div class="panel">
        <h2>数据来源</h2>
        {bar_chart(counter_items(source_counts))}
      </div>
    </section>

    <section class="panel wide">
      <h2>导出样本预览</h2>
      {sample_table(preview)}
    </section>

    <section class="panel wide">
      <h2>低质量样本预览</h2>
      {sample_table(low_quality_preview)}
    </section>
  </main>
</body>
</html>
"""


def metric_card(label: str, value: int, note: str) -> str:
    return f"""<div class="metric">
  <div class="label">{escape_html(label)}</div>
  <div class="value">{value:,}</div>
  <div class="note">{escape_html(note)}</div>
</div>"""


def counter_items(counter: Counter[str], preferred_order: list[str] | None = None) -> list[tuple[str, int]]:
    if preferred_order:
        ordered = [(key, counter.get(key, 0)) for key in preferred_order]
        extras = sorted((key, value) for key, value in counter.items() if key not in set(preferred_order))
        return ordered + extras
    return sorted(counter.items(), key=lambda item: item[1], reverse=True)


def bar_chart(items: list[tuple[str, int]]) -> str:
    if not items:
        return "<p class=\"subtitle\">暂无数据</p>"
    max_value = max(value for _, value in items) or 1
    rows = []
    for label, value in items:
        width = max(1, round(value / max_value * 100)) if value else 0
        rows.append(
            f"""<div class="bar-row">
  <div class="bar-label" title="{escape_html(label)}">{escape_html(label)}</div>
  <div class="bar-track"><div class="bar-fill" style="width: {width}%"></div></div>
  <div class="bar-value">{value:,}</div>
</div>"""
        )
    return "\n".join(rows)


def sample_table(records: list[dict[str, object]]) -> str:
    if not records:
        return "<p class=\"subtitle\">暂无样本</p>"
    rows = []
    for record in records:
        question = str(record.get("question", record.get("instruction", "")))[:90]
        answer = str(record.get("answer", record.get("output", "")))[:120]
        rows.append(
            f"""<tr>
  <td>{escape_html(str(record.get("id", "-")))}</td>
  <td><span class="tag">{escape_html(str(record.get("category", "-")))}</span></td>
  <td class="score">{escape_html(str(record.get("quality_score", "-")))}</td>
  <td>{escape_html(str(record.get("quality_level", "-")))}</td>
  <td>{escape_html(question)}</td>
  <td>{escape_html(answer)}</td>
</tr>"""
        )
    return f"""<table>
  <thead><tr><th>ID</th><th>类别</th><th>分数</th><th>等级</th><th>问题</th><th>答案</th></tr></thead>
  <tbody>{''.join(rows)}</tbody>
</table>"""


def escape_html(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


if __name__ == "__main__":
    main()

