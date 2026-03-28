# Listening Machine Gate Report v1

## Gate Policy

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

这个 gate 的目标不是证明方法成立，而是先过滤掉明显不值得上人工的包。

## Decision Counts

- allow_human_review: `34`
- borderline_review_optional: `5`
- skip_human_review: `20`

## Pack Summary

### `stage0_speech_lsf_listening_pack/v7`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `86.47` / `81.05` / `97.17`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `2` / `1` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v7/balanced_strong_v7d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `86.47` / `81.05` / `97.17`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `2` / `1` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_cepstral_listening_pack/v1`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `85.23` / `77.87` / `80.74`
- top score: `100.00`
- strong/pass/borderline/fail: `6` / `0` / `2` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v7/vctk_strong_geom_v7c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `85.15` / `78.71` / `94.56`
- top score: `100.00`
- strong/pass/borderline/fail: `6` / `2` / `0` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v7/stronger_geom_v7a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `84.99` / `78.58` / `95.41`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `2` / `1` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v7/stronger_geom_v7b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `84.79` / `77.73` / `94.80`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `2` / `1` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v7/conservative_plus_v7e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `84.70` / `77.59` / `94.17`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `1` / `2` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_listening_pack/v6`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `83.17` / `74.22` / `90.72`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `3` / `0`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `8`
- strength escalation: `escalate_strength_before_next_human`

### `stage0_speech_lsf_machine_sweep_v3/order20_rescue_v3e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `82.81` / `74.67` / `78.63`
- top score: `100.00`
- strong/pass/borderline/fail: `6` / `0` / `2` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v3/vctk_rescue_plus_v3b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `81.91` / `73.09` / `77.44`
- top score: `100.00`
- strong/pass/borderline/fail: `6` / `0` / `1` / `1`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v3/masc_push_control_v3c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `81.78` / `72.97` / `77.44`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `4` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v6/lower_geom_v6b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `81.13` / `70.97` / `87.46`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `3` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v3/fem_artifact_guard_v3d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `80.71` / `70.67` / `75.69`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `2` / `1`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v3/asym_boost_v3a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `80.67` / `70.97` / `75.90`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `2` / `1`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v6/vctk_geom_focus_v6d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `80.23` / `69.53` / `85.14`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `3` / `1`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lpc_listening_pack/v2`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `80.19` / `70.49` / `75.54`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `1` / `2`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_lsf_listening_pack/v3`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `80.16` / `74.67` / `78.63`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `2` / `2` / `0`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v6/lower_geom_v6a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `79.31` / `67.81` / `84.63`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `1` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_listening_pack/v2`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `78.85` / `68.09` / `73.71`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `5`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_lsf_machine_sweep_v2/order18_vctk_rescue_v2e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `78.85` / `68.09` / `73.71`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v4/mid_only_v4b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `78.49` / `71.29` / `76.28`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `1` / `1` / `1`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v4/air_preserve_v4a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `78.10` / `70.35` / `75.51`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `1` / `2` / `1`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v2/masc_mid_focus_v2a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `77.05` / `65.31` / `70.65`
- top score: `100.00`
- strong/pass/borderline/fail: `3` / `0` / `3` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v2/order18_mid_focus_v2d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `76.95` / `65.16` / `70.74`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v4/split_band_v4d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `76.77` / `68.30` / `73.47`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v2/masc_uniform_push_v2b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `76.67` / `64.79` / `70.77`
- top score: `100.00`
- strong/pass/borderline/fail: `3` / `0` / `3` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v4/f2_focus_v4c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `76.65` / `67.95` / `73.53`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v6/lower_geom_v6c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `74.27` / `60.06` / `75.43`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `1` / `3`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_listening_pack/v1`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `73.54` / `60.31` / `65.63`
- top score: `100.00`
- strong/pass/borderline/fail: `2` / `0` / `4` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v4/conservative_air_v4e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `72.97` / `61.37` / `66.83`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v2/balanced_pull_fem_push_masc_v2c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `72.88` / `59.35` / `64.71`
- top score: `100.00`
- strong/pass/borderline/fail: `3` / `0` / `3` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v6/conservative_geom_v6e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `70.51` / `54.86` / `65.68`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v2/conservative_order18_control_v2f`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `70.07` / `55.27` / `60.80`
- top score: `92.42`
- strong/pass/borderline/fail: `3` / `0` / `2` / `3`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lpc_listening_pack/v1`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `69.41` / `54.98` / `58.67`
- top score: `100.00`
- strong/pass/borderline/fail: `2` / `0` / `4` / `2`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v5/presence_bypass_plus_v5b`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `63.41` / `49.52` / `52.06`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v5/presence_bypass_v5a`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `63.40` / `48.96` / `51.54`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v5/vctk_bypass_focus_v5d`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `62.58` / `47.60` / `50.66`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v5/f2_only_bypass_v5c`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `62.33` / `47.28` / `50.23`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_lsf_machine_sweep_v5/gentle_bypass_control_v5e`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `61.85` / `45.11` / `48.34`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_envelope_listening_pack/v4`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `58.45` / `31.19` / `60.29`
- top score: `86.50`
- strong/pass/borderline/fail: `1` / `0` / `2` / `5`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `2`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_envelope_listening_pack/v5`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `58.00` / `31.16` / `57.82`
- top score: `84.19`
- strong/pass/borderline/fail: `1` / `0` / `3` / `4`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `4`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_resonance_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `52.75` / `32.07` / `33.82`
- top score: `73.30`
- strong/pass/borderline/fail: `0` / `0` / `2` / `6`
- reviewed outcome: `reviewed_null_result`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_low_rank_envelope_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `52.72` / `31.09` / `34.92`
- top score: `60.92`
- strong/pass/borderline/fail: `0` / `0` / `2` / `6`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `50.00` / `21.44` / `43.19`
- top score: `72.98`
- strong/pass/borderline/fail: `0` / `0` / `2` / `6`
- reviewed outcome: `reviewed_null_result`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_formant_listening_pack/v2`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `49.56` / `26.21` / `32.77`
- top score: `58.39`
- strong/pass/borderline/fail: `0` / `0` / `1` / `7`
- reviewed outcome: `reviewed_null_result`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_neural_envelope_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `49.44` / `27.06` / `29.05`
- top score: `61.78`
- strong/pass/borderline/fail: `0` / `0` / `2` / `6`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_envelope_listening_pack/v3`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `47.30` / `14.92` / `43.82`
- top score: `73.59`
- strong/pass/borderline/fail: `0` / `0` / `1` / `7`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_probe_guided_envelope_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `41.62` / `15.91` / `17.86`
- top score: `53.15`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_null_result`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_world_stft_delta_listening_pack/v4`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `40.99` / `6.11` / `43.68`
- top score: `57.21`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `1`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_vtl_warping_listening_pack/v2`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `39.26` / `0.10` / `36.86`
- top score: `42.61`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `5`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_source_filter_residual_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `39.19` / `12.70` / `13.89`
- top score: `46.59`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_null_result`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_conditioned_neural_envelope_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `38.48` / `11.45` / `13.29`
- top score: `49.12`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_world_stft_delta_listening_pack/v3`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `37.77` / `0.16` / `40.56`
- top score: `43.55`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `5`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_world_stft_delta_listening_pack/v2`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `37.66` / `0.13` / `41.30`
- top score: `44.75`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_formant_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `37.42` / `8.57` / `14.26`
- top score: `42.82`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_null_result`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_world_stft_delta_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `37.16` / `0.07` / `32.30`
- top score: `43.23`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_vtl_warping_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `36.92` / `3.73` / `20.96`
- top score: `47.41`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

### `stage0_speech_conditional_envelope_transport_listening_pack/v2`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `35.64` / `7.18` / `9.63`
- top score: `45.06`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `reviewed_null_result`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

### `stage0_speech_conditional_envelope_transport_listening_pack/v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `31.76` / `1.43` / `4.44`
- top score: `33.20`
- strong/pass/borderline/fail: `0` / `0` / `0` / `8`
- reviewed outcome: `not_reviewed`
- reviewed too_weak rows: `0`
- strength escalation: `not_reviewed`

