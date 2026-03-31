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
- rvc_sid: `0`
- bigvgan_root: `F:\proj_dev\tmp\workdir4-2\external_models\bigvgan_v2_22khz_80band_256x`

## Pack Summary

- rows: `8`
- synthesis ok: `8`
- synthesis failed: `0`
- avg carrier_target_shift_score: `40.84`
- avg target_log_mel_mae: `0.7197`
- avg source_probe_self_emd: `0.010062`
- avg loudness_drift_db: `0.00`
- avg f0_drift_cents: `156.87`

## Strongest Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | shift=`70.07` | mel_mae=`1.219072` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8\target_probe_wav\libritts_r__174__174_50561_000024_000000__d665dc2840__174_50561_000024_000000.wav`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | shift=`45.57` | mel_mae=`0.921211` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8\target_probe_wav\libritts_r__2086__2086_149214_000006_000002__23f1c25eb7__2086_149214_000006_000002.wav`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`45.28` | mel_mae=`0.458240` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8\target_probe_wav\vctk_corpus_0_92__p231__p231_011_mic1__986481509c__p231_011_mic1.wav`

## Weakest Rows

- `stage0_speech_lsf_vctk_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`27.96` | mel_mae=`1.085481` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8\target_probe_wav\vctk_corpus_0_92__p230__p230_107_mic1__8330d16640__p230_107_mic1.wav`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.75` | mel_mae=`0.302276` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8\target_probe_wav\vctk_corpus_0_92__p226__p226_011_mic1__8ef2d6c73f__p226_011_mic1.wav`
- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`34.70` | mel_mae=`0.425003` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8\target_probe_wav\vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2__p241_005_mic1.wav`
