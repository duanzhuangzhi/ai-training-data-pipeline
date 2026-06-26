# GitHub 投递说明

## 能不能直接把所有文件传 GitHub？

不能直接传全部大文件。

当前本地生成的百万级数据文件很大：

| 文件 | 大小 |
| --- | ---: |
| `data/raw/generated_qa_corpus.jsonl` | 约 737 MB |
| `data/processed/cleaned_samples.jsonl` | 约 790 MB |
| `data/processed/scored_samples.jsonl` | 约 735 MB |
| `data/exports/instruction_dataset.jsonl` | 约 717 MB |

GitHub 普通仓库会阻止超过 100 MiB 的单文件。因此 GitHub 仓库应该提交代码、文档、报告、小样例和生成脚本，而不是直接提交完整百万数据。

## 推荐投递结构

GitHub 仓库提交：

- `README.md`
- `SUBMISSION_GUIDE.md`
- `GITHUB_SUBMISSION.md`
- `pyproject.toml`
- `scripts/`
- `src/`
- `tests/`
- `docs/`
- `data/raw/demo_qa.jsonl`
- `data/raw/demo_extra.csv`
- `data/raw/extra_notes.txt`
- `data/raw/SOURCE_MANIFEST.md`
- `data/exports/instruction_dataset.sample.jsonl`
- `reports/data_quality_report.md`
- `reports/dashboard.html`

不直接提交：

- `data/raw/generated_qa_corpus.jsonl`
- `data/processed/*.jsonl`
- `data/exports/instruction_dataset.jsonl`

## 招聘方怎么看到百万数据？

README 里说明：

```powershell
python scripts/make_demo_dataset.py
python scripts/run_pipeline.py
```

这两条命令可以在本地复现 1,000,000 条原始数据和完整处理结果。

如果对方需要查看完整文件，可以补充：

- GitHub Release 附件
- Git LFS
- 百度网盘/阿里云盘链接
- 只上传压缩后的结果文件到云盘

## 投递时附上的链接

建议投递时写：

> GitHub：项目代码、文档、运行脚本和小样例  
> 本地已完成百万级数据处理，README 中提供复现命令；完整大文件可按需通过网盘或 Git LFS 提供。

## 推荐截图

1. GitHub README 首页。
2. 本地终端百万数据运行结果。
3. `reports/data_quality_report.md` 数据质量报告。
4. `data/raw` 文件大小截图，证明百万数据真实生成。
5. `reports/dashboard.html` 可视化看板。
6. `scripts/run_pipeline.py` 和 `src/ai_data_pipeline/pipeline.py` 关键代码截图。
