# 听审流程调整：Machine-First Review Gate v1

## 背景

到 `2026-03-28` 为止，表示层主线已经出现一个很明确的问题：

- 多条方法虽然已经能稳定出包、出量化、出 GUI；
- 但其中大量包在机器侧先验明显偏弱时，人工听审仍然反复给出 `8/8 no audible`。

这意味着当前若继续默认“每出一包就直接上人工”，时间成本已经明显高于信息增益。

## 新默认流程

从这个断点开始，新的默认流程改成：

1. 先建包；
2. 先跑量化队列；
3. 先过 machine gate；
4. 只有 machine gate 通过，才进入正式人工听审；
5. 若 machine gate 不通过，则优先继续 machine-only 迭代，不立即上人工。

## v1 Gate 阈值

当前 `v1` 采用偏保守阈值：

- `avg_auto_quant_score >= 65`
- `avg_auto_direction_score >= 45`
- `avg_auto_effect_score >= 45`
- 并且满足以下至少一条：
  - `top_auto_quant_score >= 75`
  - `strongish_rows >= 2`

其中 `strongish_rows = strong_pass + pass + borderline`。

## 这组阈值的目的

这组阈值不是为了证明方法成立，而是为了回答更窄的问题：

**这个包是否已经强到值得花人工听一轮。**

它允许以下情况继续存在：

- 高机器分但人耳觉得是“错误变化”；
- 高机器分但最终被主观否掉。

但它会尽量避免继续出现以下情况：

- 机器侧长期 `40~55` 分、全包 `fail=8`；
- 人工再花一轮时间后，仍然只是 `8/8 no audible`。

## 当前配套脚本

- 机器 gate 汇总脚本：`scripts/build_listening_machine_gate_report.py`
- 当前报告落点：`artifacts/machine_gate/v1/`

## 当前结论

在现有历史包上回放这套 gate 后：

- `allow_human_review = 4`
- `skip_human_review = 20`

这说明当前人工听审口径确实应该收紧。

## 对主线的直接影响

1. `source-filter residual v1` 虽然已经完成人工听审并确认 `8/8 no audible`，但按新流程它本来就不该进入人工：
   - `avg_auto_quant_score ≈ 39.19`
   - `avg_auto_direction_score ≈ 12.70`
   - `avg_auto_effect_score ≈ 13.89`
2. 后续新包若 machine gate 不通过，默认不再直接开 GUI 做正式听审。
3. 后续主线应先切到“machine-only 搜索下一条高先验候选”，而不是继续扩大人工审听覆盖面。
