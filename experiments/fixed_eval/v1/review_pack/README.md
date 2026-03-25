# review_pack

## 文件说明

- `review_queue_v1.csv`
  - 推荐直接在 GUI 中打开的主队列，已经按 triage 优先级和风险分数排序。
- `priority_high.csv`
  - 最值得先听的一批样本，通常包含低响度、高静音比、低有声比或特征提取异常。
- `priority_medium.csv`
  - 次优先级样本，建议在 high 听完后处理。
- `priority_low.csv`
  - 没有明显自动特征异常，但仍建议最终过一遍。

## 推荐流程

1. 先运行 `scripts/open_fixed_eval_review_gui.ps1`。
2. GUI 默认读取 `review_queue_v1.csv`，从高优先级未审样本开始。
3. 如只想先做粗筛，也可以直接先听 `priority_high.csv` 里的样本。

## triage 规则

- `high`
  - 特征提取失败，或出现明显低响度 / 高静音比 / 低有声比。
- `medium`
  - 有轻到中度异常迹象，建议排在 `high` 之后。
- `low`
  - 暂无明显异常，只需做常规人工确认。
