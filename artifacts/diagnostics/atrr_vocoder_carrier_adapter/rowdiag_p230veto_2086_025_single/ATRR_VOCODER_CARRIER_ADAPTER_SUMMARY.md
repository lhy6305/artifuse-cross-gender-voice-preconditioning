# ATRR Vocoder Carrier Adapter Probe v1

## Scope

- This run validates the carrier adapter boundary only.
- It is not a human-review candidate.
- The current backend is the local `bigvgan_v2_22khz_80band_256x` generator.
- This is a mel-native GAN vocoder with a backend domain close to the exported target packages.

## Parameters

- backend: `bigvgan_local_v1`
- griffinlim_iter: `64`
- n_fft: `2048`
- hop_length: `256`
- n_mels: `80`
- match_source_rms: `True`
- pitch_correct_source_median: `True`
- pitch_correct_voiced_only: `False`
- pitch_correct_min_drift_cents: `150.0`
- pitch_correct_max_cents: `200.0`
- pitch_correct_crossfade_ms: `25.0`
- pitch_correct_min_span_ms: `80.0`
- voiced_target_blend_alpha: `0.75`
- frame_distribution_anchor_alpha: `0.75`
- frame_anchor_l1_threshold: `None`
- frame_anchor_min_alpha: `0.0`
- target_bin_delta_threshold: `None`
- target_bin_delta_threshold_masculine: `0.01`
- target_bin_delta_threshold_feminine: `0.015`
- target_bin_delta_threshold_masculine_low_f0: `None`
- target_bin_delta_threshold_masculine_mid_f0: `None`
- target_bin_delta_threshold_masculine_high_f0: `None`
- target_bin_delta_threshold_feminine_low_f0: `None`
- target_bin_delta_threshold_feminine_mid_f0: `None`
- target_bin_delta_threshold_feminine_high_f0: `None`
- target_bin_shape_topk_count: `3`
- target_bin_shape_topk_sum_cutoff: `None`
- target_bin_delta_threshold_feminine_sharp: `None`
- target_bin_source_emd_cutoff: `None`
- target_bin_delta_threshold_masculine_weak: `None`
- target_bin_delta_threshold_feminine_weak: `None`
- target_bin_record_override: `['libritts_r__2086__2086_149214_000006_000002__23f1c25eb7=0.025']`
- target_bin_record_veto: `['vctk_corpus_0_92__p230__p230_107_mic1__8330d16640']`
- target_bin_occupancy_threshold: `0.05`
- rvc_sid: `0`
- bigvgan_root: `F:\proj_dev\tmp\workdir4-2\external_models\bigvgan_v2_22khz_80band_256x`

## Pack Summary

- rows: `1`
- synthesis ok: `1`
- synthesis failed: `0`
- avg carrier_target_shift_score: `43.31`
- avg target_log_mel_mae: `0.8648`
- avg source_probe_self_emd: `0.002865`
- avg loudness_drift_db: `0.00`
- avg f0_drift_cents: `5.01`

## Strongest Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | shift=`43.31` | mel_mae=`0.864774` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\rowdiag_p230veto_2086_025_single\target_probe_wav\libritts_r__2086__2086_149214_000006_000002__23f1c25eb7__2086_149214_000006_000002.wav`

## Weakest Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | shift=`43.31` | mel_mae=`0.864774` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\rowdiag_p230veto_2086_025_single\target_probe_wav\libritts_r__2086__2086_149214_000006_000002__23f1c25eb7__2086_149214_000006_000002.wav`
