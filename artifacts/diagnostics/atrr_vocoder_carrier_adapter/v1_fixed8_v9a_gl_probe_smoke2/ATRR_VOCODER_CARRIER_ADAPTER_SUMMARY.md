# ATRR Vocoder Carrier Adapter Probe v1

## Scope

- This run validates the carrier adapter boundary only.
- It is not a human-review candidate.
- The current backend is `griffinlim_mel_probe`, used as a bounded mel-to-wave probe.
- Local RVC generators were inspected but are not directly compatible with the exported target packages because they expect Hubert-style content features plus F0 and speaker conditioning, not standalone edited log-mel tensors.

## Parameters

- backend: `griffinlim_mel_probe`
- griffinlim_iter: `64`
- n_fft: `2048`
- hop_length: `256`
- n_mels: `80`

## Pack Summary

- rows: `2`
- synthesis ok: `2`
- synthesis failed: `0`
- avg carrier_target_shift_score: `55.25`
- avg target_log_mel_mae: `0.3543`
- avg source_probe_self_emd: `0.003012`
- avg loudness_drift_db: `-0.11`
- avg f0_drift_cents: `7.50`

## Strongest Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`55.62` | mel_mae=`0.373809` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_gl_probe_smoke2\target_probe_wav\stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`54.88` | mel_mae=`0.334710` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_gl_probe_smoke2\target_probe_wav\stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a.wav`

## Weakest Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`54.88` | mel_mae=`0.334710` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_gl_probe_smoke2\target_probe_wav\stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a.wav`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | shift=`55.62` | mel_mae=`0.373809` | target_wav=`F:\proj_dev\tmp\workdir4-2\artifacts\diagnostics\atrr_vocoder_carrier_adapter\v1_fixed8_v9a_gl_probe_smoke2\target_probe_wav\stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a.wav`
