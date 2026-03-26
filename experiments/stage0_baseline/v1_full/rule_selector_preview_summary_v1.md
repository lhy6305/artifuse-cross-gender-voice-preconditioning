# Rule Selector Preview Summary v1

## 输入

- 配置：`rule_candidate_v1.json`
- 预览输入：`clean_singing_enriched.csv`
- selector：`scripts/select_stage0_candidate_rules.py`

## 总覆盖率

- `feminine` 方向：`927 / 2038`，约 `45.49%`
- `masculine` 方向：`605 / 2038`，约 `29.69%`

## feminine 覆盖率按 style

- `fast_forte`：`166 / 332`，`50.0%`
- `fast_piano`：`160 / 320`，`50.0%`
- `slow_forte`：`175 / 350`，`50.0%`
- `slow_piano`：`175 / 352`，约 `49.7%`
- `straight`：`149 / 300`，约 `49.7%`
- `vibrato`：`102 / 204`，`50.0%`
- `forte`：`0 / 90`
- `pp`：`0 / 90`

## masculine 覆盖率按 style

- `slow_forte`：`175 / 350`，`50.0%`
- `slow_piano`：`177 / 352`，约 `50.3%`
- `straight`：`151 / 300`，约 `50.3%`
- `vibrato`：`102 / 204`，`50.0%`
- `fast_forte`：`0 / 332`
- `fast_piano`：`0 / 320`
- `forte`：`0 / 90`
- `pp`：`0 / 90`

## 当前结论

- `median_split` 型规则基本按预期命中对应一半样本。
- 女性向规则当前集中在高区提亮，因此 `fast_*` 只有 `feminine` 方向有覆盖。
- 男性向规则当前集中在低区压亮，因此 `slow_*`、`straight`、`vibrato` 才有 `masculine` 覆盖。
- `forte` 与 `pp` 仍保持排除状态，当前 preview 没有误命中。

## 下一步

1. 如果后续进入最小前置器原型，可先只对 preview 已覆盖的 style 开启。
2. 如果要扩大 `masculine` 方向覆盖率，可再评估是否保留 `fast_* low_band` 的女性向规则以外的补充项。
3. `forte` 与 `pp` 仍应继续保持观察态，暂不纳入常规启用配置。
