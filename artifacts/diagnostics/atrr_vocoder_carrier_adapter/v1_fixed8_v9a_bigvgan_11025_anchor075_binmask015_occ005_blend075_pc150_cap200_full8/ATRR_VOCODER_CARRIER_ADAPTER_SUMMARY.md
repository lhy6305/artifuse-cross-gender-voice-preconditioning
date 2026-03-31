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
- target_bin_delta_threshold: `0.015`
- target_bin_occupancy_threshold: `0.05`
- rvc_sid: `0`
- bigvgan_root: `F:\proj_dev\tmp\workdir4-2\external_models\bigvgan_v2_22khz_80band_256x`

## Pack Summary

- rows: `8`
- synthesis ok: `8`
- synthesis failed: `0`
- avg carrier_target_shift_score: `39.73`
- avg target_log_mel_mae: `0.5442`
- avg source_probe_self_emd: `0.010062`
- avg loudness_drift_db: `0.00`
- avg f0_drift_cents: `140.63`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`56.65` | mel_mae=`0.317543` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_anchor075_binmask015_occ005_blend075_pc150_cap200_full8\target_probe_wav\vctk_corpus_0_92__p226__p226_011_mic1__8ef2d6c73f__p226_011_mic1.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`50.64` | mel_mae=`0.467030` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_anchor075_binmask015_occ005_blend075_pc150_cap200_full8\target_probe_wav\libritts_r__1919__1919_142785_000089_000003__11e66c65d9__1919_142785_000089_000003.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`49.70` | mel_mae=`0.437418` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_anchor075_binmask015_occ005_blend075_pc150_cap200_full8\target_probe_wav\libritts_r__1995__1995_1826_000022_000000__82d5a66723__1995_1826_000022_000000.wav`

## Weakest Rows

- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`25.30` | mel_mae=`0.386191` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_anchor075_binmask015_occ005_blend075_pc150_cap200_full8\target_probe_wav\vctk_corpus_0_92__p231__p231_011_mic1__986481509c__p231_011_mic1.wav`
- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`25.80` | mel_mae=`0.365644` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_anchor075_binmask015_occ005_blend075_pc150_cap200_full8\target_probe_wav\vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2__p241_005_mic1.wav`
- `stage0_speech_lsf_vctk_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`28.10` | mel_mae=`1.091644` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_anchor075_binmask015_occ005_blend075_pc150_cap200_full8\target_probe_wav\vctk_corpus_0_92__p230__p230_107_mic1__8330d16640__p230_107_mic1.wav`
