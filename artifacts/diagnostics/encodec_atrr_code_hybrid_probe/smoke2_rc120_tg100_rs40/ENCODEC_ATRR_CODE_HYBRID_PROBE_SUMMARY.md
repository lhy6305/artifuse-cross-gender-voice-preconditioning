# Encodec ATRR Code Hybrid Probe Summary v1

- rows: `1`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- quantizer_range: `[24, 32)`
- avg target_logmel_delta_l1_db: `0.0987`
- avg scaffold_teacher_gap_rms: `0.0440`
- avg residual_correction_rms: `0.0113`
- avg final_teacher_gap_rms: `0.0439`
- avg changed_code_ratio: `0.1850`
- avg teacher_final_mel_loss: `0.004038`
- avg teacher_final_wave_l1: `0.000286`
- avg final_mel_loss: `0.004410`
- avg final_wave_l1: `0.001022`
- avg core_mask_ratio: `0.0500`

## Strongest Residual Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | residual_rms=`0.011346` | final_gap_rms=`0.043857`

## Closest To Teacher After Correction

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | final_gap_rms=`0.043857` | changed_code_ratio=`0.184953`
