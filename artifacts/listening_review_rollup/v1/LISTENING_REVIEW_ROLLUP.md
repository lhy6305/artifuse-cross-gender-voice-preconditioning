# Listening Review Rollup v1

## Sparse Review Semantics

- `effect_audible` 是主开关。
- 当 `effect_audible` 为 `no` 或 `maybe` 时，其它空字段视为 `n/a`，不是漏填。
- 当 `effect_audible` 为 `yes` 且其它字段留空时，按用户约定解释为“该字段没有明显问题”。
- 因此本汇总会对 `direction_correct / artifact_issue / strength_fit / keep_recommendation` 生成 `norm` 字段，但不会改写原始 CSV。

## Pack Summary

### `stage0_speech_formant_listening_pack/v1`

- reviewed: `8/8`
- audible: `yes=0` `maybe=0` `no=8`
- direction: `yes=0` `maybe=0` `no=0` `n/a=8`
- artifact: `yes=0` `slight=0` `no=0` `n/a=8`
- keep: `yes=0` `maybe=0` `no=0` `n/a=8`
- strength: `ok=0` `too_weak=0` `too_strong=0` `n/a=8`
- proposed disposition: `null_result`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=0` `keep_yes=0`

### `stage0_speech_listening_pack/v1`

- reviewed: `8/8`
- audible: `yes=0` `maybe=0` `no=8`
- direction: `yes=0` `maybe=0` `no=0` `n/a=8`
- artifact: `yes=0` `slight=0` `no=0` `n/a=8`
- keep: `yes=0` `maybe=0` `no=0` `n/a=8`
- strength: `ok=0` `too_weak=0` `too_strong=0` `n/a=8`
- proposed disposition: `null_result`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=0` `keep_yes=0`

### `stage0_speech_resonance_listening_pack/v1`

- reviewed: `8/8`
- audible: `yes=0` `maybe=0` `no=8`
- direction: `yes=0` `maybe=0` `no=0` `n/a=8`
- artifact: `yes=0` `slight=0` `no=0` `n/a=8`
- keep: `yes=0` `maybe=0` `no=0` `n/a=8`
- strength: `ok=0` `too_weak=0` `too_strong=0` `n/a=8`
- proposed disposition: `null_result`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=0` `keep_yes=0`

### `stage0_speech_world_stft_delta_listening_pack/v1`

- reviewed: `8/8`
- audible: `yes=2` `maybe=2` `no=4`
- direction: `yes=2` `maybe=1` `no=0` `n/a=5`
- artifact: `yes=0` `slight=0` `no=2` `n/a=6`
- keep: `yes=2` `maybe=0` `no=0` `n/a=6`
- strength: `ok=0` `too_weak=4` `too_strong=0` `n/a=4`
- proposed disposition: `watch`
- implicit fills from audible=yes: `direction_yes=2` `artifact_no=2` `strength_ok=0` `keep_yes=2`

