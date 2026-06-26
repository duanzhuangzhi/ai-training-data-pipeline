# 数据集设计说明

上一版项目只有十几条样例数据，确实更像演示骨架，不足以证明“能处理数据系统”。现在项目增加了 `scripts/make_demo_dataset.py`，用于生成一批更接近真实处理场景的原始数据。

## 为什么使用自建 demo 数据

这个项目用于求职展示，数据要能公开放到 GitHub，同时不能涉及隐私、版权或不合规采集。因此当前版本使用自建中文问答数据来模拟真实 AI 数据 pipeline 中的典型问题。

这比直接爬一批未知网页更稳：面试时可以清楚解释数据结构、噪声设计和清洗目标。

## 数据规模

生成脚本默认创建 1,000,000 条原始样本，再叠加少量手写 JSONL、CSV、TXT 样例。数据量用于展示百万级批处理能力，噪声类型用于展示清洗、去重、筛选和质量报告能力。

## 覆盖的数据问题

| 数据类型 | 用途 |
| --- | --- |
| 正常问答 | 导出高质量 instruction 数据 |
| 精确重复 | 验证完全重复去重 |
| 近似重复 | 验证相似文本去重 |
| HTML 残留 | 验证网页清洗能力 |
| 广告营销 | 验证低质量内容识别 |
| 空字段 | 验证无效样本过滤 |
| 过短答案 | 验证信息量过滤 |
| 异常字符 | 验证噪声比例检测 |

## 为什么这对岗位有价值

招聘描述看重的不是“手动清理几行数据”，而是能不能把混乱数据变成可复用流程。这个数据集故意包含多种脏数据，让 pipeline 能展示：

- 数据导入能力
- 清洗规则设计
- 去重策略
- 质量评分
- 类别统计
- 训练格式导出
- 质量报告生成

## 如何重新生成数据

```powershell
python scripts/make_demo_dataset.py
python scripts/run_pipeline.py
python scripts/build_dashboard.py
```

如果只想快速验证流程，可以先生成小规模数据：

```powershell
python scripts/make_demo_dataset.py --records 1000
python scripts/run_pipeline.py
python scripts/build_dashboard.py
```
