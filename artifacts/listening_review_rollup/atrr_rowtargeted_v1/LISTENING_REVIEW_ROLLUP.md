# Listening Review Rollup v1

## Sparse Review Semantics

- `effect_audible` 是主开关。
- 当 `effect_audible` 为 `no` 或 `maybe` 时，其它空字段视为 `n/a`，不是漏填。
- 当 `effect_audible` 为 `yes` 且其它字段留空时，按用户约定解释为“该字段没有明显问题”。
- 因此本汇总会对 `direction_correct / artifact_issue / strength_fit / keep_recommendation` 生成 `norm` 字段，但不会改写原始 CSV。

## Pack Summary

### `stage0_atrr_vocoder_bigvgan_fixed8/rowveto_p230_override2086_025_v1`

- reviewed: `8/8`
- audible: `yes=7` `maybe=0` `no=1`
- direction: `yes=0` `maybe=1` `no=6` `n/a=1`
- artifact: `yes=7` `slight=0` `no=1` `n/a=0`
- keep: `yes=0` `maybe=0` `no=0` `n/a=8`
- strength: `ok=7` `too_weak=0` `too_strong=0` `n/a=1`
- proposed disposition: `reject`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=7` `keep_yes=0`

