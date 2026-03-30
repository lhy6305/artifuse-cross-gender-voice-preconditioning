# Listening Review Rollup v1

## Sparse Review Semantics

- `effect_audible` 是主开关。
- 当 `effect_audible` 为 `no` 或 `maybe` 时，其它空字段视为 `n/a`，不是漏填。
- 当 `effect_audible` 为 `yes` 且其它字段留空时，按用户约定解释为“该字段没有明显问题”。
- 因此本汇总会对 `direction_correct / artifact_issue / strength_fit / keep_recommendation` 生成 `norm` 字段，但不会改写原始 CSV。

## Pack Summary

### `stage0_speech_lsf_listening_pack/v8`

- reviewed: `8/8`
- audible: `yes=6` `maybe=2` `no=0`
- direction: `yes=2` `maybe=4` `no=0` `n/a=2`
- artifact: `yes=0` `slight=5` `no=2` `n/a=1`
- keep: `yes=2` `maybe=0` `no=0` `n/a=6`
- strength: `ok=3` `too_weak=3` `too_strong=0` `n/a=2`
- proposed disposition: `watch_with_risk`
- implicit fills from audible=yes: `direction_yes=2` `artifact_no=1` `strength_ok=3` `keep_yes=2`

