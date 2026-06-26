# 投递材料准备指南

这份项目可以直接对应招聘方提到的加分材料。

## 1. 简历项目名称

中文 AI 问答训练数据清洗与筛选系统

## 2. 简历项目描述

构建中文 AI 问答训练数据清洗与筛选系统，实现从多源数据导入、标准化清洗、重复检测、质量评分、主题分类到 instruction 数据集导出的自动化 pipeline。设计长度、广告词、异常字符、问答匹配度等质量规则，输出数据质量报告和可复用训练数据格式，体现 AI 训练数据构建、数据质量控制和工程化流程设计能力。

## 3. 简历要点 bullet

- 设计并实现多源数据导入模块，支持 JSONL、CSV、TXT 三类原始问答数据统一转换为标准结构。
- 构建 100 万条中文问答 demo 数据集，覆盖正常样本、精确重复、近似重复、HTML 残留、广告噪声、空字段和过短回答等场景。
- 实现数据清洗与质量控制规则，包括 HTML 清理、空值过滤、重复样本检测、广告噪声识别和异常字符检测。
- 构建训练数据质量评分机制，将样本分为 high、medium、low 三档，并记录可追溯的过滤原因。
- 输出 instruction 微调格式 JSONL 文件和 Markdown 数据质量报告，展示原始样本数、去重率、类别分布和质量分布。
- 使用模块化代码和自动化脚本串联完整 pipeline，便于后续接入 pandas、向量相似度模型或调度系统。
- 将 pipeline 改造为流式处理，百万级数据不需要一次性全部加载进内存，并在运行日志中按 10 万条输出处理进度。

## 4. 面试讲法

可以这样讲：

> 我做这个项目不是为了单次清洗数据，而是模拟真实 AI 训练数据构建流程。原始数据进来后，系统会先统一结构，再做清洗、去重、质量评分、主题分类，最后导出 instruction 数据集和质量报告。每一步都有中间产物，方便排查问题和复用流程。

如果面试官问为什么不用更复杂的模型：

> 当前版本为了保证环境稳定，先用标准库实现了规则和轻量相似度去重。后续可以把近似去重替换成 sentence-transformers 向量召回，把分类模块替换成开源文本分类模型。

## 5. 建议截图

建议准备 4 张截图：

1. 项目目录结构截图，证明它不是单文件脚本。
2. 运行 `python scripts/make_demo_dataset.py` 和 `python scripts/run_pipeline.py` 的终端结果截图。
3. `reports/data_quality_report.md` 的报告截图。
4. `data/exports/instruction_dataset.jsonl` 的训练集样例截图。
5. `data/raw/SOURCE_MANIFEST.md` 的数据来源和噪声设计截图。
6. `reports/dashboard.html` 的可视化看板截图。

## 6. GitHub README 展示重点

README 首页建议让对方第一眼看到：

- 项目解决什么问题。
- pipeline 流程图或步骤。
- 快速运行命令。
- 输出文件示例。
- 与岗位加分项的对应关系。

## 7. 后续增强方向

- 接入 requests + BeautifulSoup 做公开网页采集。
- 使用 pandas 处理更大规模 CSV 数据。
- 使用 sentence-transformers 做向量相似去重。
- 使用 Streamlit 做交互式数据质量面板；当前项目已提供无依赖静态版 `reports/dashboard.html`。
- 使用 APScheduler 或 Airflow 做定时调度。
