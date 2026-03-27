# Listening Review Rollup v1

## Sparse Review Semantics

- `effect_audible` 是主开关。
- 当 `effect_audible` 为 `no` 或 `maybe` 时，其它空字段视为 `n/a`，不是漏填。
- 当 `effect_audible` 为 `yes` 且其它字段留空时，按用户约定解释为“该字段没有明显问题”。
- 因此本汇总会对 `direction_correct / artifact_issue / strength_fit / keep_recommendation` 生成 `norm` 字段，但不会改写原始 CSV。

## Pack Summary

### `stage0_speech_cepstral_listening_pack/v1`

- reviewed: `8/8`
- audible: `yes=1` `maybe=4` `no=3`
- direction: `yes=0` `maybe=4` `no=0` `n/a=4`
- artifact: `yes=0` `slight=3` `no=1` `n/a=4`
- keep: `yes=1` `maybe=0` `no=0` `n/a=7`
- strength: `ok=0` `too_weak=4` `too_strong=0` `n/a=4`
- proposed disposition: `watch_with_risk`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=1` `strength_ok=0` `keep_yes=1`

### `stage0_speech_envelope_listening_pack/v3`

- reviewed: `8/8`
- audible: `yes=3` `maybe=0` `no=5`
- direction: `yes=0` `maybe=3` `no=0` `n/a=5`
- artifact: `yes=0` `slight=3` `no=0` `n/a=5`
- keep: `yes=0` `maybe=1` `no=0` `n/a=7`
- strength: `ok=3` `too_weak=0` `too_strong=0` `n/a=5`
- proposed disposition: `watch_with_risk`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=3` `keep_yes=0`

### `stage0_speech_envelope_listening_pack/v4`

- reviewed: `8/8`
- audible: `yes=6` `maybe=1` `no=1`
- direction: `yes=0` `maybe=2` `no=4` `n/a=2`
- artifact: `yes=0` `slight=3` `no=3` `n/a=2`
- keep: `yes=1` `maybe=0` `no=0` `n/a=7`
- strength: `ok=4` `too_weak=2` `too_strong=0` `n/a=2`
- proposed disposition: `reject`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=3` `strength_ok=4` `keep_yes=1`

### `stage0_speech_envelope_listening_pack/v5`

- reviewed: `8/8`
- audible: `yes=5` `maybe=0` `no=3`
- direction: `yes=5` `maybe=0` `no=0` `n/a=3`
- artifact: `yes=0` `slight=2` `no=4` `n/a=2`
- keep: `yes=4` `maybe=0` `no=0` `n/a=4`
- strength: `ok=1` `too_weak=4` `too_strong=0` `n/a=3`
- proposed disposition: `watch_with_risk`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=3` `strength_ok=1` `keep_yes=4`

### `stage0_speech_formant_listening_pack/v1`

- reviewed: `8/8`
- audible: `yes=0` `maybe=0` `no=8`
- direction: `yes=0` `maybe=0` `no=0` `n/a=8`
- artifact: `yes=0` `slight=0` `no=0` `n/a=8`
- keep: `yes=0` `maybe=0` `no=0` `n/a=8`
- strength: `ok=0` `too_weak=0` `too_strong=0` `n/a=8`
- proposed disposition: `null_result`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=0` `keep_yes=0`

### `stage0_speech_formant_listening_pack/v2`

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

### `stage0_speech_lpc_listening_pack/v1`

- reviewed: `8/8`
- audible: `yes=0` `maybe=4` `no=4`
- direction: `yes=0` `maybe=2` `no=0` `n/a=6`
- artifact: `yes=0` `slight=0` `no=0` `n/a=8`
- keep: `yes=0` `maybe=0` `no=0` `n/a=8`
- strength: `ok=0` `too_weak=8` `too_strong=0` `n/a=0`
- proposed disposition: `watch`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=0` `keep_yes=0`

### `stage0_speech_lpc_listening_pack/v2`

- reviewed: `8/8`
- audible: `yes=5` `maybe=2` `no=1`
- direction: `yes=0` `maybe=5` `no=0` `n/a=3`
- artifact: `yes=1` `slight=5` `no=0` `n/a=2`
- keep: `yes=0` `maybe=0` `no=0` `n/a=8`
- strength: `ok=5` `too_weak=0` `too_strong=0` `n/a=3`
- proposed disposition: `reject`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=5` `keep_yes=0`

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

### `stage0_speech_world_stft_delta_listening_pack/v2`

- reviewed: `8/8`
- audible: `yes=0` `maybe=4` `no=4`
- direction: `yes=0` `maybe=0` `no=0` `n/a=8`
- artifact: `yes=0` `slight=2` `no=1` `n/a=5`
- keep: `yes=0` `maybe=0` `no=0` `n/a=8`
- strength: `ok=0` `too_weak=0` `too_strong=0` `n/a=8`
- proposed disposition: `watch_with_risk`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=0` `keep_yes=0`

### `stage0_speech_world_stft_delta_listening_pack/v3`

- reviewed: `8/8`
- audible: `yes=4` `maybe=2` `no=2`
- direction: `yes=5` `maybe=0` `no=0` `n/a=3`
- artifact: `yes=0` `slight=0` `no=4` `n/a=4`
- keep: `yes=4` `maybe=0` `no=0` `n/a=4`
- strength: `ok=0` `too_weak=5` `too_strong=0` `n/a=3`
- proposed disposition: `watch`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=4` `strength_ok=0` `keep_yes=4`

### `stage0_speech_world_stft_delta_listening_pack/v4`

- reviewed: `8/8`
- audible: `yes=4` `maybe=4` `no=0`
- direction: `yes=1` `maybe=4` `no=0` `n/a=3`
- artifact: `yes=4` `slight=4` `no=0` `n/a=0`
- keep: `yes=0` `maybe=0` `no=0` `n/a=8`
- strength: `ok=3` `too_weak=1` `too_strong=0` `n/a=4`
- proposed disposition: `reject`
- implicit fills from audible=yes: `direction_yes=0` `artifact_no=0` `strength_ok=3` `keep_yes=0`

