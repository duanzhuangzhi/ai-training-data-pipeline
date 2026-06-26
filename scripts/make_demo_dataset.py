from __future__ import annotations

import argparse
import json
from pathlib import Path


TOPICS = {
    "data_cleaning": [
        (
            "如何设计一套可复用的数据清洗流程？",
            "可以先统一字段结构，再按空值、重复值、格式异常、长度异常和业务规则拆分清洗函数。每一步都要输出处理数量和过滤原因，方便复查和复用。",
        ),
        (
            "数据去重为什么不能只用完全相等判断？",
            "真实数据里经常存在标点、空格、换行和措辞差异，完全相等只能发现一部分重复。更稳妥的方式是先做规范化，再结合 n-gram 或向量相似度识别近似重复。",
        ),
        (
            "如何判断问答数据是否适合进入训练集？",
            "可以检查问题是否明确、答案是否完整、是否包含广告噪声、是否存在乱码、问答是否相关，以及样本是否和已有数据高度重复。",
        ),
        (
            "数据质量报告应该展示哪些指标？",
            "建议展示原始样本数、清洗后样本数、过滤原因、重复率、质量等级分布、类别分布、平均长度和导出样本数量。",
        ),
        (
            "清洗规则为什么要记录过滤原因？",
            "记录过滤原因可以让数据处理过程可追溯。后续如果导出样本数量异常，或者某类数据被过度过滤，就能快速定位是哪条规则产生了影响。",
        ),
    ],
    "crawler": [
        (
            "写网页采集脚本时要注意什么？",
            "要先确认数据可以被合规使用，控制请求频率，设置超时和重试，并保存来源链接、采集时间和页面字段，方便后续追踪数据来源。",
        ),
        (
            "爬虫采集下来的 HTML 为什么不能直接入库？",
            "HTML 里通常包含标签、脚本、导航、广告和不可见字符，需要先抽取正文，再做文本规范化，否则会污染训练数据并影响模型学习。",
        ),
        (
            "自动化采集失败时应该怎么处理？",
            "应该记录失败 URL、异常类型和重试次数，避免静默失败。对于连续失败的数据源，可以暂停任务并输出告警或人工复核清单。",
        ),
        (
            "如何避免采集任务产生大量重复数据？",
            "可以对 URL、标题、正文摘要分别建立去重 key，并在采集后用文本相似度做二次去重，保留来源更可信或内容更完整的样本。",
        ),
        (
            "采集数据为什么要保留 metadata？",
            "metadata 可以保存来源、时间、栏目和原始字段。数据出现质量问题时，metadata 能帮助定位问题源头，也能支持按来源评估数据质量。",
        ),
    ],
    "ai_training": [
        (
            "什么是 instruction 数据集？",
            "instruction 数据集通常包含指令、输入和输出三部分，用来训练模型按照用户要求完成任务。问答数据经过整理后可以转换成 instruction 格式。",
        ),
        (
            "训练数据中混入广告内容会有什么影响？",
            "广告样本会给模型带来错误表达模式，可能让模型生成营销话术、无关链接或低质量回答，所以需要在入库前识别并过滤。",
        ),
        (
            "为什么 AI 训练数据要做质量分层？",
            "质量分层可以让高质量样本直接进入训练集，中等样本进入人工抽检，低质量样本默认过滤，从而降低人工审核成本。",
        ),
        (
            "如何用开源模型增强数据筛选？",
            "可以使用 sentence-transformers 做语义相似去重，用文本分类模型判断主题，用规则和模型结果结合生成质量评分。",
        ),
        (
            "问答样本的答案过长一定好吗？",
            "不一定。答案过长可能混入网页正文、多个问题或无关背景。训练数据更看重准确、完整和针对性，而不是单纯追求长度。",
        ),
    ],
    "engineering": [
        (
            "数据 pipeline 为什么要分模块？",
            "分模块可以让导入、清洗、去重、评分、分类、导出和报告各自独立，便于测试、替换和排查问题，也更接近真实工程项目。",
        ),
        (
            "日志在数据处理项目里有什么作用？",
            "日志可以记录每一步输入输出数量、耗时和异常信息。当处理结果异常时，可以通过日志判断问题出现在导入、清洗还是导出环节。",
        ),
        (
            "批处理脚本需要支持哪些参数？",
            "至少应该支持输入路径、输出路径、最低导出分数和是否覆盖结果。这样同一套脚本可以处理不同批次的数据。",
        ),
        (
            "为什么中间产物也要保存？",
            "保存中间产物可以让处理流程可复盘。比如清洗后数据、评分后数据和最终导出数据分别保存，方便定位样本在哪一步被改变。",
        ),
        (
            "如何证明自己不是只会手工处理数据？",
            "可以展示自动化脚本、模块化代码、质量报告、异常样本统计和导出格式，让别人看到你能把数据问题沉淀成稳定流程。",
        ),
    ],
    "career": [
        (
            "AI 数据工程岗位项目应该怎么讲？",
            "重点讲清楚数据来源、处理流程、质量规则、自动化脚本和最终产物。不要只说用了什么工具，要说明为什么这样设计。",
        ),
        (
            "投递时项目截图应该截哪些内容？",
            "可以截图项目目录、脚本运行结果、质量报告、导出数据样例和关键代码模块，让招聘方快速看到项目完整度。",
        ),
        (
            "没有真实公司经历可以做什么项目？",
            "可以做一个模拟真实业务流程的数据 pipeline，用公开或自建样例数据覆盖采集、清洗、筛选、导出和报告生成。",
        ),
        (
            "简历里如何描述数据清洗项目？",
            "不要只写清洗数据，而要写清楚处理规模、清洗规则、质量指标、自动化程度、最终输出和对后续模型训练的价值。",
        ),
        (
            "面试官问项目难点时怎么回答？",
            "可以回答难点在于数据噪声类型多、重复样本不完全一致、质量规则需要可解释，以及处理流程必须可复用和可追溯。",
        ),
    ],
}

DOMAINS = ["招聘问答", "课程内容", "日志分析", "网页采集", "模型训练", "数据标注", "知识库", "运营报表"]
SCENES = ["离线批处理", "每日增量", "人工复核", "训练集构建", "质量抽检", "自动化调度", "异常回溯", "结果导出"]

NOISY_RECORDS = [
    ("免费领取 Python 资料是真的吗？", "免费领取资料，加微信 123456，点击链接马上领取，限时优惠。", "spam"),
    ("怎么快速变强？", "私信我，三天掌握 AI 数据工程，包就业，名额有限。", "spam"),
    ("数据清洗", "很好。", "too_short"),
    ("AI", "模型。", "too_short"),
    ("<h1>如何处理 HTML 残留？</h1>", "<p>先移除标签，再反转义 HTML 实体，例如 &amp;nbsp; 和 &lt;br&gt;，最后统一空白。</p>", "html"),
    ("乱码样本如何识别？", "正常文本中如果混入 @@@###￥￥￥%%%% 这类异常符号比例过高，就应该进入人工复核或过滤。", "noise"),
    ("", "这个样本没有问题字段，应该被清洗模块过滤。", "invalid"),
    ("问题为空答案也无意义", "", "invalid"),
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a large demo QA corpus.")
    parser.add_argument("--records", type=int, default=1_000_000, help="Number of records to generate.")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    raw_dir = project_root / "data" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    output_path = raw_dir / "generated_qa_corpus.jsonl"
    with output_path.open("w", encoding="utf-8") as file:
        previous_base: dict[str, object] | None = None
        for index in range(1, args.records + 1):
            record = build_record(index, previous_base)
            if record["metadata"].get("noise_type") not in {"exact_duplicate", "near_duplicate"}:
                previous_base = record
            file.write(json.dumps(record, ensure_ascii=False) + "\n")

    manifest_path = raw_dir / "SOURCE_MANIFEST.md"
    manifest_path.write_text(build_manifest(args.records), encoding="utf-8")

    print(f"Generated {args.records} records")
    print(f"Dataset: {output_path}")
    print(f"Manifest: {manifest_path}")


def build_record(index: int, previous_base: dict[str, object] | None) -> dict[str, object]:
    if index % 113 == 0:
        question, answer, noise_type = NOISY_RECORDS[(index // 113) % len(NOISY_RECORDS)]
        return {
            "id": f"noise-{index:07d}",
            "source": "synthetic_noise_corpus",
            "question": question,
            "answer": answer,
            "metadata": {
                "topic": "noise",
                "noise_type": noise_type,
                "license": "self-created demo data",
            },
        }

    if previous_base and index % 29 == 0:
        duplicate = dict(previous_base)
        duplicate["id"] = f"dup-{index:07d}"
        duplicate["metadata"] = dict(previous_base["metadata"])
        duplicate["metadata"]["noise_type"] = "exact_duplicate"
        return duplicate

    if previous_base and index % 31 == 0:
        near = dict(previous_base)
        near["id"] = f"near-{index:07d}"
        near["question"] = str(previous_base["question"]).replace("如何", "怎么").replace("为什么", "为啥")
        near["answer"] = str(previous_base["answer"]).replace("可以", "建议").replace("需要", "要")
        near["metadata"] = dict(previous_base["metadata"])
        near["metadata"]["noise_type"] = "near_duplicate"
        return near

    topic_names = list(TOPICS)
    topic = topic_names[index % len(topic_names)]
    pairs = TOPICS[topic]
    pair_no = index % len(pairs)
    round_no = (index // len(pairs)) % 97 + 1
    question, answer = pairs[pair_no]
    domain = DOMAINS[index % len(DOMAINS)]
    scene = SCENES[(index // 7) % len(SCENES)]
    return {
        "id": f"seed-{index:07d}",
        "source": "synthetic_million_corpus",
        "question": f"{add_variant(question, round_no)} 场景：{domain}-{scene}-{index:07d}",
        "answer": f"{add_answer_context(answer, topic, round_no)} 当前样本来自 {domain} 的{scene}场景，批次编号为 batch-{index:07d}。",
        "metadata": {
            "topic": topic,
            "batch": round_no,
            "pair_no": pair_no + 1,
            "domain": domain,
            "scene": scene,
            "license": "self-created demo data",
        },
    }


def add_variant(question: str, round_no: int) -> str:
    prefixes = ["", "在项目里，", "面向 AI 训练数据时，", "批量处理时，", "从工程角度看，", "做 Demo 时，"]
    suffixes = ["", "请给出具体做法。", "有哪些注意点？", "怎么落地？", "如何验证效果？", "怎么写进简历？"]
    return f"{prefixes[(round_no - 1) % len(prefixes)]}{question}{suffixes[round_no % len(suffixes)]}"


def add_answer_context(answer: str, topic: str, round_no: int) -> str:
    contexts = [
        "实际处理时还要保留原始 ID 和来源字段，避免后续无法追溯。",
        "如果数据量变大，可以把这一步拆成批处理任务，并记录日志。",
        "为了便于面试展示，最好同时输出中间文件和最终报告。",
        "这类规则要尽量可解释，方便人工审核样本时理解系统判断。",
        "后续可以接入向量模型或调度系统，把规则处理升级成更完整的数据平台。",
        "在项目说明里，需要写清楚输入、处理逻辑、输出和评估指标。",
    ]
    return f"{answer}{contexts[(round_no - 1) % len(contexts)]} 主题标签：{topic}。"


def build_manifest(record_count: int) -> str:
    return f"""# 原始数据说明

本目录包含项目演示用原始数据，共 {record_count:,} 条自动生成的中文问答样本，加上少量手写 JSONL、CSV、TXT 样例。

## 数据设计目的

这批数据不是随便填充的占位内容，而是为了模拟 AI 训练数据构建中常见的数据状态：

- 正常问答样本：用于导出 instruction 训练数据。
- 精确重复样本：测试 exact duplicate 去重。
- 近似重复样本：测试 n-gram 相似去重。
- HTML 残留样本：测试标签清理和 HTML 实体反转义。
- 广告/营销样本：测试低质量内容识别。
- 空字段和过短回答：测试无效样本过滤。
- 异常字符样本：测试噪声比例检测。

## 数据来源

当前数据为自建 demo 数据，默认生成 1,000,000 条，适合公开放到 GitHub 展示，不涉及个人隐私或版权采集风险。

如果后续要扩展为真实项目，可以把公开数据或合规网页采集结果转换成同样的字段结构：

```json
{{"id":"xxx","source":"xxx","question":"...","answer":"...","metadata":{{"url":"..."}}}}
```
"""


if __name__ == "__main__":
    main()
