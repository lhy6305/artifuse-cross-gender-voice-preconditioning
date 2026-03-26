# Stage 0 候选规则配置格式 v1

## 当前产物

当前已经有两份可直接消费的候选规则配置：

- `experiments/stage0_baseline/v1_full/rule_candidate_v1.csv`
- `experiments/stage0_baseline/v1_full/rule_candidate_v1.json`
- `experiments/stage0_baseline/v1_full/rule_selector_preview_summary_v1.md`

对应生成脚本：

- `scripts/build_stage0_rule_candidate_config.py`
- `scripts/select_stage0_candidate_rules.py`

## 选择边界

当前配置只保留：

- `singing` 域
- `fast_forte`
- `fast_piano`
- `slow_forte`
- `slow_piano`
- `straight`
- `vibrato`

并额外约束：

- `high_band` 只保留 `feminine` 方向
- `low_band` 只保留 `masculine` 方向
- `forte` / `pp` 暂不进入常规候选配置
- `speech` 暂不进入常规候选配置

## CSV 字段

`rule_candidate_v1.csv` 当前字段如下：

- `rule_id`
- `enabled`
- `domain`
- `group_axis`
- `group_value`
- `f0_condition`
- `bucket_scheme`
- `signal_name`
- `target_direction`
- `action_family`
- `strength_label`
- `alpha_default`
- `alpha_max`
- `confidence`
- `priority`
- `source_status`
- `notes`

## JSON 结构

`rule_candidate_v1.json` 当前结构分为：

1. `config_version`
2. `source`
3. `selection_policy`
4. `strength_presets`
5. `rules`

其中每条 `rules` 项包含：

- `rule_id`
- `enabled`
- `match`
- `signal_name`
- `target_direction`
- `action_family`
- `strength`
- `confidence`
- `priority`
- `notes`

`match` 子对象当前固定包含：

- `domain`
- `group_axis`
- `group_value`
- `f0_condition`
- `bucket_scheme`

`strength` 子对象当前固定包含：

- `label`
- `alpha_default`
- `alpha_max`

## 当前强度预设

当前只是保守上限建议，不是最终 DSP 参数：

- `weak`：`alpha_default=0.12`，`alpha_max=0.18`
- `medium`：`alpha_default=0.18`，`alpha_max=0.28`
- `medium_high`：`alpha_default=0.24`，`alpha_max=0.34`
- `high`：`alpha_default=0.30`，`alpha_max=0.42`

## 推荐使用方式

如果后续开始写最小规则前置器，推荐优先使用 `rule_candidate_v1.json`：

- `selection_policy` 可直接反映当前启用边界
- `strength_presets` 已经内嵌
- `rules` 结构适合直接做匹配与开关控制

如果后续主要做人工审核或表格迭代，优先使用 `rule_candidate_v1.csv`。

如果后续要先做规则命中验证或批量预览，直接使用：

- `scripts/select_stage0_candidate_rules.py`

当前已有一轮 `clean_singing_v1` preview 摘要：

- `experiments/stage0_baseline/v1_full/rule_selector_preview_summary_v1.md`

## 下一步

当前配置格式已经够支撑下一轮：

1. 把候选规则接到最小规则前置器原型。
2. 为每条规则补更细的频带或 gain 解释。
3. 如需扩展到 `speech`，先在配置层之外完成一致性验证，再纳入 `rules`。
