# Encodec ATRR Code Refit Probe Summary v1

- rows: `8`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- quantizer_range: `[24, 32)`
- avg target_logmel_delta_l1_db: `0.0678`
- avg teacher_projection_rms: `0.0354`
- avg teacher_projection_l1: `0.0142`
- avg changed_code_ratio: `0.1548`
- avg teacher_final_mel_loss: `0.004540`
- avg teacher_final_wave_l1: `0.000333`
- avg core_mask_ratio: `0.0609`

## Strongest Teacher Projection Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | projection_rms=`0.043971` | changed_code_ratio=`0.184953`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | projection_rms=`0.043894` | changed_code_ratio=`0.161141`
- `libritts_r__174__174_50561_000024_000000__d665dc2840` | projection_rms=`0.043043` | changed_code_ratio=`0.164919`

## Highest Changed-Code Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | changed_code_ratio=`0.184953` | projection_l1=`0.019333`
- `libritts_r__174__174_50561_000024_000000__d665dc2840` | changed_code_ratio=`0.164919` | projection_l1=`0.019616`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | changed_code_ratio=`0.161141` | projection_l1=`0.020350`
