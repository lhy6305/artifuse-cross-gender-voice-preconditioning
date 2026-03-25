# fixed_eval v1

## 文件说明

- `fixed_eval_manifest_v1.csv`
  - 固定评测集 v1 的基础清单。
- `fixed_eval_manifest_v1_enriched.csv`
  - 在基础清单上补了轻量声学特征，适合先做自动筛查和人工听检前排序。
- `fixed_eval_review_sheet_v1.csv`
  - 人工巡检工作表，默认所有样本的 `review_status` 都是 `pending`。

## 推荐使用顺序

1. 先看 `fixed_eval_manifest_v1_enriched.csv`，按 `feature_status`、`rms_dbfs`、`silence_ratio_40db`、`f0_voiced_ratio` 排查明显异常。
2. 再在 `fixed_eval_review_sheet_v1.csv` 里做人工听检，把不可用样本标出来。
3. 如果人工听检淘汰了样本，不直接手改基础清单，优先在 review sheet 中记录，再决定是否重抽 v1.1 或升级到 v2。
