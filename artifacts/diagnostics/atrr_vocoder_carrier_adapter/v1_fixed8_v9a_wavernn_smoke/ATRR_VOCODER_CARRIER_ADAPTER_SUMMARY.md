# ATRR Vocoder Carrier Adapter Probe v1

## Scope

- This run validates the carrier adapter boundary only.
- It is not a human-review candidate.
- The current backend is the pretrained `torchaudio` WaveRNN vocoder bundle.
- This is the first true mel-native neural vocoder backend on the active route.

## Parameters

- backend: `torchaudio_wavernn_bridge_v1`
- griffinlim_iter: `64`
- n_fft: `2048`
- hop_length: `256`
- n_mels: `80`
- rvc_sid: `0`

## Pack Summary

- rows: `2`
- synthesis ok: `2`
- synthesis failed: `0`
- avg carrier_target_shift_score: `0.00`
- avg target_log_mel_mae: `2.7844`
- avg source_probe_self_emd: `0.047281`
- avg loudness_drift_db: `7.12`
- avg f0_drift_cents: `2742.51`

## Strongest Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`2.793965` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_wavernn_smoke\target_probe_wav\libritts_r__1919__1919_142785_000089_000003__11e66c65d9__1919_142785_000089_000003.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`2.774817` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_wavernn_smoke\target_probe_wav\libritts_r__1995__1995_1826_000022_000000__82d5a66723__1995_1826_000022_000000.wav`

## Weakest Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`2.793965` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_wavernn_smoke\target_probe_wav\libritts_r__1919__1919_142785_000089_000003__11e66c65d9__1919_142785_000089_000003.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`0.00` | mel_mae=`2.774817` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_wavernn_smoke\target_probe_wav\libritts_r__1995__1995_1826_000022_000000__82d5a66723__1995_1826_000022_000000.wav`
