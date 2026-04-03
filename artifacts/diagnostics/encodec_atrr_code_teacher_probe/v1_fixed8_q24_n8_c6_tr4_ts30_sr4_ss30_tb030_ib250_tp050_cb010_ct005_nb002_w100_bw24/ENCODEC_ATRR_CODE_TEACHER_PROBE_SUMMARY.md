# Encodec ATRR Code Teacher Probe Summary v1

- rows: `8`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- quantizer_range: `[24, 32)`
- candidate_count: `6`
- avg target_logmel_delta_l1_db: `0.0678`
- avg teacher_projection_rms: `0.0334`
- avg teacher_projection_l1: `0.0190`
- avg nonbase_mass: `0.2680`
- avg base_choice_prob: `0.7320`
- avg teacher_final_mel_loss: `0.004478`
- avg teacher_final_wave_l1: `0.000345`
- avg final_wave_l1: `0.001058`
- avg core_mask_ratio: `0.0609`

## Strongest Teacher-Gap Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | projection_rms=`0.043863` | nonbase=`0.293522`
- `libritts_r__174__174_50561_000024_000000__d665dc2840` | projection_rms=`0.043561` | nonbase=`0.284971`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | projection_rms=`0.037591` | nonbase=`0.253007`

## Highest Non-Base Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | nonbase=`0.293522` | base_prob=`0.706478`
- `libritts_r__174__174_50561_000024_000000__d665dc2840` | nonbase=`0.284971` | base_prob=`0.715029`
- `vctk_corpus_0_92__p226__p226_011_mic1__8ef2d6c73f` | nonbase=`0.274233` | base_prob=`0.725767`
