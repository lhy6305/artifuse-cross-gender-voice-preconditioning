# Listening Review Rollup v1

## Sparse Review Semantics

- `effect_audible` 是主开关。
- 当 `effect_audible` 为 `no` 或 `maybe` 时，其它空字段视为 `n/a`，不是漏填。
- 当 `effect_audible` 为 `yes` 且其它字段留空时，按用户约定解释为“该字段没有明显问题”。
- 因此本汇总会对 `direction_correct / artifact_issue / strength_fit / keep_recommendation` 生成 `norm` 字段，但不会改写原始 CSV。

## Pack Summary

### `stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a`

- reviewed: `8/8`
- audible: `yes=0` `maybe=2` `no=6`
- direction: `yes=0` `maybe=0` `no=0` `n/a=8`
- artifact: `yes=0` `slight=0` `no=0` `n/a=8`
- keep: `yes=0` `maybe=0` `no=0` `n/a=8`
- strength: `ok=0` `too_weak=4` `too_strong=0` `n/a=4`
- proposed disposition: `watch`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=0` `keep_yes=0`

