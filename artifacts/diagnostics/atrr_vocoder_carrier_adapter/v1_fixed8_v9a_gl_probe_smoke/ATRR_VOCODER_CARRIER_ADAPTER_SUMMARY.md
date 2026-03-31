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
- synthesis ok: `0`
- synthesis failed: `2`
- avg carrier_target_shift_score: `n/a`
- avg target_log_mel_mae: `n/a`
- avg source_probe_self_emd: `n/a`
- avg loudness_drift_db: `n/a`
- avg f0_drift_cents: `n/a`

## Strongest Rows


## Weakest Rows


## Failures

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | error=`rule_id not found in queue csv`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | error=`rule_id not found in queue csv`
