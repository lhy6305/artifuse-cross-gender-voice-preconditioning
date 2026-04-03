# Encodec ATRR Code Gate Probe Summary v1

- rows: `1`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- quantizer_range: `[24, 32)`
- avg target_logmel_delta_l1_db: `0.0987`
- avg teacher_code_gap_rms: `0.0468`
- avg teacher_code_gap_l1: `0.0210`
- avg gate_mean: `0.1090`
- avg base_keep_mean: `0.8910`
- avg teacher_final_mel_loss: `0.004039`
- avg teacher_final_wave_l1: `0.000286`
- avg final_wave_l1: `0.000108`
- avg core_mask_ratio: `0.0500`

## Largest Teacher-Code Gap Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | gap_rms=`0.046841` | gate_mean=`0.109007`

## Highest Gate Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | gate_mean=`0.109007` | base_keep=`0.890993`
