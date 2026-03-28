# Listening Machine Gate Report v1

## Gate Policy

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

这个 gate 的目标不是证明方法成立，而是先过滤掉明显不值得上人工的包。

## Decision Counts

- allow_human_review: `4`
- borderline_review_optional: `0`
- skip_human_review: `20`

## Pack Summary

### `stage0_speech_cepstral_listening_pack/v1`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `85.23` / `77.87` / `80.74`
- top score: `100.00`
- strong/pass/borderline/fail: `6` / `0` / `2` / `0`
- reviewed outcome: `not_reviewed`

### `stage0_speech_lpc_listening_pack/v2`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `80.19` / `70.49` / `75.54`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `1` / `2`
- reviewed outcome: `reviewed_non_null`

### `stage0_speech_lsf_listening_pack/v1`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `73.54` / `60.31` / `65.63`
- top score: `100.00`
- strong/pass/borderline/fail: `2` / `0` / `4` / `2`
- reviewed outcome: `not_reviewed`

### `stage0_speech_lpc_listening_pack/v1`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `69.41` / `54.98` / `58.67`
- top score: `100.00`
- strong/pass/borderline/fail: `2` / `0` / `4` / `2`
- reviewed outcome: `not_reviewed`

### `stage0_speech_envelope_listening_pack/v4`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `58.45` / `31.19` / `60.29`
- top score: `86.50`
- strong/pass/borderline/fail: `1` / `0` / `2` / `5`
- reviewed outcome: `reviewed_non_null`

### `stage0_speech_envelope_listening_pack/v5`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `58.00` / `31.16` / `57.82`
- top score: `84.19`
- strong/pass/borderline/fail: `1` / `0` / `3` / `4`
- reviewed outcome: `reviewed_non_null`

### `stage0_speech_resonance_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `52.75` / `32.07` / `33.82`
- top score: `73.30`
- strong/pass/borderline/fail: `0` / `0` / `2` / `6`
- reviewed outcome: `reviewed_null_result`

### `stage0_speech_low_rank_envelope_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `52.72` / `31.09` / `34.92`
- top score: `60.92`
- strong/pass/borderline/fail: `0` / `0` / `2` / `6`
- reviewed outcome: `not_reviewed`

### `stage0_speech_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `50.00` / `21.44` / `43.19`
- top score: `72.98`
- strong/pass/borderline/fail: `0` / `0` / `2` / `6`
- reviewed outcome: `reviewed_null_result`

### `stage0_speech_formant_listening_pack/v2`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `49.56` / `26.21` / `32.77`
- top score: `58.39`
- strong/pass/borderline/fail: `0` / `0` / `1` / `7`
- reviewed outcome: `reviewed_null_result`

### `stage0_speech_neural_envelope_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `49.44` / `27.06` / `29.05`
- top score: `61.78`
- strong/pass/borderline/fail: `0` / `0` / `2` / `6`
- reviewed outcome: `not_reviewed`

### `stage0_speech_envelope_listening_pack/v3`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `47.30` / `14.92` / `43.82`
- top score: `73.59`
- strong/pass/borderline/fail: `0` / `0` / `1` / `7`
- reviewed outcome: `reviewed_non_null`

### `stage0_speech_probe_guided_envelope_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `41.62` / `15.91` / `17.86`
- top score: `53.15`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_null_result`

### `stage0_speech_world_stft_delta_listening_pack/v4`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `40.99` / `6.11` / `43.68`
- top score: `57.21`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_non_null`

### `stage0_speech_vtl_warping_listening_pack/v2`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `39.26` / `0.10` / `36.86`
- top score: `42.61`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_non_null`

### `stage0_speech_source_filter_residual_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `39.19` / `12.70` / `13.89`
- top score: `46.59`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_null_result`

### `stage0_speech_conditioned_neural_envelope_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `38.48` / `11.45` / `13.29`
- top score: `49.12`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `not_reviewed`

### `stage0_speech_world_stft_delta_listening_pack/v3`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `37.77` / `0.16` / `40.56`
- top score: `43.55`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_non_null`

### `stage0_speech_world_stft_delta_listening_pack/v2`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `37.66` / `0.13` / `41.30`
- top score: `44.75`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_non_null`

### `stage0_speech_formant_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `37.42` / `8.57` / `14.26`
- top score: `42.82`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_null_result`

### `stage0_speech_world_stft_delta_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `37.16` / `0.07` / `32.30`
- top score: `43.23`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `not_reviewed`

### `stage0_speech_vtl_warping_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `36.92` / `3.73` / `20.96`
- top score: `47.41`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `not_reviewed`

### `stage0_speech_conditional_envelope_transport_listening_pack/v2`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `35.64` / `7.18` / `9.63`
- top score: `45.06`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_null_result`

### `stage0_speech_conditional_envelope_transport_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `31.76` / `1.43` / `4.44`
- top score: `33.20`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `not_reviewed`

