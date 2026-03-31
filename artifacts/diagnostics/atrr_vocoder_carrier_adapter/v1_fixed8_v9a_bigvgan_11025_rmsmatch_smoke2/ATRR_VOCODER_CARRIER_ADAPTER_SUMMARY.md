# ATRR Vocoder Carrier Adapter Probe v1

## Scope

- This run validates the carrier adapter boundary only.
- It is not a human-review candidate.
- The current backend is the local `BigVGAN v2 22khz 80band fmax8k 256x` generator.
- This is a mel-native GAN vocoder with a backend domain close to the exported target packages.

## Parameters

- backend: `bigvgan_local_v1`
- griffinlim_iter: `64`
- n_fft: `2048`
- hop_length: `256`
- n_mels: `80`
- match_source_rms: `True`
- rvc_sid: `0`

## Pack Summary

- rows: `2`
- synthesis ok: `2`
- synthesis failed: `0`
- avg carrier_target_shift_score: `26.72`
- avg target_log_mel_mae: `0.4799`
- avg source_probe_self_emd: `0.002965`
- avg loudness_drift_db: `0.00`
- avg f0_drift_cents: `240.00`

## Strongest Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`30.45` | mel_mae=`0.491465` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_rmsmatch_smoke2\target_probe_wav\libritts_r__1919__1919_142785_000089_000003__11e66c65d9__1919_142785_000089_000003.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`22.99` | mel_mae=`0.468431` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_rmsmatch_smoke2\target_probe_wav\libritts_r__1995__1995_1826_000022_000000__82d5a66723__1995_1826_000022_000000.wav`

## Weakest Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`22.99` | mel_mae=`0.468431` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_rmsmatch_smoke2\target_probe_wav\libritts_r__1995__1995_1826_000022_000000__82d5a66723__1995_1826_000022_000000.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`30.45` | mel_mae=`0.491465` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_bigvgan_11025_rmsmatch_smoke2\target_probe_wav\libritts_r__1919__1919_142785_000089_000003__11e66c65d9__1919_142785_000089_000003.wav`
