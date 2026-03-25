# 任务与分支映射

## 当前状态
- 当前仓库还处于开题与整备阶段，没有必须绑定到真实 Git 分支的并行开发流。
- 本文档先记录任务切分和建议边界，等后续出现实际分支后再补充映射关系。

## 当前任务切分

| 任务 | 目标 | 当前状态 | 主要落点 |
|---|---|---|---|
| 仓库整备 | 固定文档入口、编码规范、Git 边界 | 已完成第二轮 | `docs/`、`.gitignore`、`.gitattributes`、`.editorconfig` |
| 实验记录骨架 | 固定日报、实验记录、关键 checkpoint 落位 | 已完成首轮 | `reports/daily/`、`experiments/`、`artifacts/checkpoints/keep/` |
| 环境冻结 | 固定 Python/Torch/音频处理环境 | 已完成首轮 | `docs/15_stage0_runtime_environment_v1.md`、`requirements-stage0-analysis.txt` |
| 第三方依赖边界 | 明确上游 RVC 代码是参考副本还是纳管依赖 | 待开始 | `third_party/` 或根目录参考位点 |
| 数据资产盘点 | 建立数据总表与评测集方案 | 已完成首轮 | `data/datasets/_meta/`、`docs/12_dataset_inventory_first_pass.md` |
| 固定评测集 v1 | 冻结第一版评测桶、配额、规则与清单 | 已完成首轮 | `docs/13_fixed_eval_sampling_v1.md`、`scripts/sample_fixed_eval_set.py`、`experiments/fixed_eval/v1/` |
| 人工巡检工具链 | 用最少操作完成 fixed eval 听审与记录 | 已完成首轮 | `scripts/open_fixed_eval_review_gui.ps1`、`scripts/fixed_eval_review_gui.py`、`experiments/fixed_eval/v1/review_pack/` |
| clean analysis subsets | 生成保守可复现的 speech / singing 主分析子集 | 已完成首轮 | `scripts/build_clean_analysis_subsets.py`、`data/datasets/_meta/utterance_manifest_clean_*.csv`、`docs/14_clean_analysis_subsets_v1.md` |
| 分析脚本落地 | 实现阶段 0/1 所需预处理与统计脚本 | 已完成首轮 | `scripts/run_stage0_baseline_analysis.py`、`docs/16_stage0_baseline_analysis_v1.md`、`experiments/stage0_baseline/` |

## 分支建议
- 如果后续开始多人或多任务并行，优先按任务边界拆分，而不是按文件类型拆分。
- 建议优先出现的分支方向：
  - `task/stage0-full-analysis`
  - `task/analysis-reporting`
  - `task/manifest-feature-expansion`
- 只有在出现真实分支后，才在这里登记“分支名 -> 任务 -> 涉及文件”的映射。
