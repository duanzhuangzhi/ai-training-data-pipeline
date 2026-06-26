# Million-Scale AI Training Data Pipeline

百万级中文 AI 问答训练数据清洗、筛选、质量评估与 instruction 格式导出项目。

这个项目模拟 AI 数据工程岗位中的训练数据构建流程：原始问答数据存在重复、广告噪声、HTML 残留、空字段、过短回答和异常字符等问题，pipeline 会将这些原始数据加工成可用于大模型微调的高质量 instruction 数据集，并生成数据质量报告和可视化 Dashboard。

## 项目结果

本地已完成百万级数据处理：

```text
Raw samples: 1,000,014
Cleaned samples: 995,292
Deduped samples: 926,121
Exported samples: 926,118
```

核心产物：

- 数据质量报告：`reports/data_quality_report.md`
- 可视化看板：`reports/dashboard.html`
- 小样例训练集：`data/exports/instruction_dataset.sample.jsonl`
- 百万数据生成脚本：`scripts/make_demo_dataset.py`
- 完整 pipeline：`scripts/run_pipeline.py`

> GitHub 普通仓库不适合直接提交 700MB 级 JSONL 大文件。本仓库提交代码、说明、报告、Dashboard 和小样例；百万级完整数据可通过脚本本地复现。

## 这个项目解决什么问题

AI 模型不能直接使用原始脏数据训练。真实业务数据里常见问题包括：

- 问题或答案为空
- 回答过短，没有训练价值
- 内容重复或近似重复
- 混入广告、营销话术
- 网页采集残留 HTML 标签
- 存在异常字符或乱码
- 数据来源和处理过程不可追溯

本项目把这些问题拆成可复用的数据处理流程：

```text
原始问答数据
    ↓
多源导入 JSONL / CSV / TXT
    ↓
文本清洗与无效样本过滤
    ↓
精确去重 + 近似去重
    ↓
质量评分 + 问题记录
    ↓
主题分类
    ↓
instruction 数据集导出
    ↓
质量报告 + Dashboard
```

## 数据是什么，怎么来的

数据是自建中文问答 demo 数据集，由脚本自动生成：

```powershell
python scripts/make_demo_dataset.py
```

默认生成 1,000,000 条样本，并混入多种真实 pipeline 中会遇到的数据问题：

| 数据类型 | 目的 |
| --- | --- |
| 正常问答 | 导出高质量 instruction 训练数据 |
| 精确重复 | 测试 exact duplicate 去重 |
| 近似重复 | 测试相似文本去重 |
| HTML 残留 | 测试网页文本清洗 |
| 广告营销 | 测试低质量内容识别 |
| 空字段 | 测试无效样本过滤 |
| 过短答案 | 测试信息量过滤 |
| 异常字符 | 测试噪声检测 |

使用自建数据的原因：适合公开放到 GitHub，不涉及隐私、版权或非法采集风险，同时能稳定复现百万级数据处理结果。

## 快速运行

当前版本只使用 Python 标准库，无需安装额外依赖。

```powershell
cd ai-data-pipeline
python scripts/make_demo_dataset.py
python scripts/run_pipeline.py
python scripts/build_dashboard.py
```

快速验证可以生成 1000 条小数据：

```powershell
python scripts/make_demo_dataset.py --records 1000
python scripts/run_pipeline.py
python scripts/build_dashboard.py
```

## 输出文件

| 文件 | 说明 |
| --- | --- |
| `data/raw/generated_qa_corpus.jsonl` | 百万级原始问答数据，本地生成，不提交 GitHub |
| `data/processed/cleaned_samples.jsonl` | 清洗后中间数据，本地生成 |
| `data/processed/scored_samples.jsonl` | 评分后中间数据，本地生成 |
| `data/exports/instruction_dataset.jsonl` | 完整 instruction 训练数据，本地生成 |
| `data/exports/instruction_dataset.sample.jsonl` | GitHub 展示用小样例 |
| `reports/data_quality_report.md` | 数据质量报告 |
| `reports/dashboard.html` | 静态可视化 Dashboard |

## 技术实现

- `src/ai_data_pipeline/loaders.py`：多源数据导入，支持 JSONL、CSV、TXT。
- `src/ai_data_pipeline/cleaning.py`：HTML 清理、文本规范化、无效样本过滤。
- `src/ai_data_pipeline/dedupe.py`：精确去重和轻量近似去重。
- `src/ai_data_pipeline/scoring.py`：质量评分、问题记录、主题分类。
- `src/ai_data_pipeline/pipeline.py`：流式 pipeline 主流程，避免百万数据一次性进入内存。
- `scripts/build_dashboard.py`：读取处理结果并生成静态质量看板。

## 项目亮点

- 百万级数据处理：默认生成并处理 1,000,000 条中文问答样本。
- 流式处理：逐条读取、清洗、评分和写出，适合大文件处理。
- 可解释质量控制：每条低质量样本记录扣分原因。
- 训练集导出：输出大模型微调常用 instruction JSONL 格式。
- 可视化展示：生成 HTML Dashboard，便于投递截图和面试讲解。
- GitHub 友好：大文件由脚本复现，仓库只保存代码、文档、报告和样例。

## 简历描述

构建百万级中文 AI 问答训练数据清洗与筛选 pipeline，使用 Python 实现多源数据导入、文本清洗、无效样本过滤、精确/近似去重、质量评分、主题分类、instruction 格式导出和可视化质量看板。项目处理 100 万+ 原始样本，清洗后保留 99.5 万条，去重后导出 92.6 万条训练样本，并生成数据质量报告用于追踪过滤原因、类别分布和质量等级。

## 面试讲法

我做这个项目是为了模拟 AI 数据工程里的训练数据构建流程。模型不能直接使用原始脏数据，所以我搭建了一个 pipeline：先生成/导入原始问答数据，再清洗 HTML、空值、短回答和广告噪声，然后做精确和近似去重，再给样本打质量分和分类，最后导出 instruction 数据集、质量报告和可视化 Dashboard。

