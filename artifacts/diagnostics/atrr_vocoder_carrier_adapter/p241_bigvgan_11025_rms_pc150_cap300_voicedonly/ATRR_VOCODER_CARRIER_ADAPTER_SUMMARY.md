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
- pitch_correct_voiced_only: `True`
- pitch_correct_min_drift_cents: `150.0`
- pitch_correct_max_cents: `300.0`
- pitch_correct_crossfade_ms: `25.0`
- pitch_correct_min_span_ms: `80.0`
- rvc_sid: `0`
- bigvgan_root: `F:\proj_dev\tmp\workdir4-2\external_models\bigvgan_v2_22khz_80band_256x`

## Pack Summary

- rows: `1`
- synthesis ok: `1`
- synthesis failed: `0`
- avg carrier_target_shift_score: `23.37`
- avg target_log_mel_mae: `0.7976`
- avg source_probe_self_emd: `0.019929`
- avg loudness_drift_db: `0.00`
- avg f0_drift_cents: `640.00`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`23.37` | mel_mae=`0.797582` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\p241_bigvgan_11025_rms_pc150_cap300_voicedonly\target_probe_wav\vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2__p241_005_mic1.wav`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`23.37` | mel_mae=`0.797582` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\p241_bigvgan_11025_rms_pc150_cap300_voicedonly\target_probe_wav\vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2__p241_005_mic1.wav`
