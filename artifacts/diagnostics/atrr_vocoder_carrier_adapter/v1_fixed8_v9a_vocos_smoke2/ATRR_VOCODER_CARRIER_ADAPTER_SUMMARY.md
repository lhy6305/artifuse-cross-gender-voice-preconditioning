# ATRR Vocoder Carrier Adapter Probe v1

## Scope

- This run validates the carrier adapter boundary only.
- It is not a human-review candidate.
- The current backend is the local `Vocos mel 24khz` model.
- This is a Fourier-domain mel-native vocoder with a local checkpoint and local config.

## Parameters

- backend: `vocos_local_v1`
- griffinlim_iter: `64`
- n_fft: `2048`
- hop_length: `256`
- n_mels: `80`
- match_source_rms: `False`
- rvc_sid: `0`

## Pack Summary

- rows: `2`
- synthesis ok: `2`
- synthesis failed: `0`
- avg carrier_target_shift_score: `0.00`
- avg target_log_mel_mae: `4.7010`
- avg source_probe_self_emd: `0.042727`
- avg loudness_drift_db: `-30.53`
- avg f0_drift_cents: `1167.51`

## Strongest Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`4.663385` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_vocos_smoke2\target_probe_wav\libritts_r__1919__1919_142785_000089_000003__11e66c65d9__1919_142785_000089_000003.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`4.738541` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_vocos_smoke2\target_probe_wav\libritts_r__1995__1995_1826_000022_000000__82d5a66723__1995_1826_000022_000000.wav`

## Weakest Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`4.663385` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_vocos_smoke2\target_probe_wav\libritts_r__1919__1919_142785_000089_000003__11e66c65d9__1919_142785_000089_000003.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`4.738541` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_vocos_smoke2\target_probe_wav\libritts_r__1995__1995_1826_000022_000000__82d5a66723__1995_1826_000022_000000.wav`
