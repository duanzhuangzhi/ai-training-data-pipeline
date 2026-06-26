# 数据质量报告

- 生成时间: 2026-06-26 14:02:54
- 原始样本数: 1000014
- 清洗后样本数: 995292
- 去重后样本数: 926121
- 最终导出训练样本数: 926118

## 清洗过滤统计

| 原因 | 数量 |
| --- | ---: |
| empty_question | 1180 |
| empty_answer | 1181 |
| too_short_answer | 2361 |
| kept | 995292 |

## 去重统计

| 类型 | 数量 |
| --- | ---: |
| exact_duplicates | 38514 |
| near_duplicates | 30657 |
| kept | 926121 |

## 质量等级分布

| 等级 | 数量 |
| --- | ---: |
| high | 926117 |
| medium | 1 |
| low | 3 |

## 类别分布

| 类别 | 数量 |
| --- | ---: |
| ai | 90574 |
| data | 653258 |
| general | 3 |
| tech | 182286 |

## 质量问题统计

| 问题 | 数量 |
| --- | ---: |
| answer_too_short | 1 |
| high_abnormal_char_ratio | 2 |
| spam_or_marketing | 3 |
| weak_question_answer_overlap | 3 |

## 样本预览

| ID | 类别 | 分数 | 等级 | 问题 |
| --- | --- | ---: | --- | --- |
| csv-001 | data | 100 | high | 如何做文本相似去重? |
| csv-002 | data | 100 | high | 项目截图应该展示什么? |
| demo-001 | data | 100 | high | 如何学习 Python 数据清洗? |
| demo-002 | ai | 100 | high | AI 训练数据为什么要做去重? |
| demo-003 | data | 90 | high | 爬虫项目要注意什么? |
| demo-004 | data | 82 | high | 数据质量报告应该包含哪些指标? |
| demo-005 | data | 100 | high | 怎么把数据处理流程做成系统? |
| demo-006 | general | 55 | low | 免费领取资料加微信是真的吗? |
