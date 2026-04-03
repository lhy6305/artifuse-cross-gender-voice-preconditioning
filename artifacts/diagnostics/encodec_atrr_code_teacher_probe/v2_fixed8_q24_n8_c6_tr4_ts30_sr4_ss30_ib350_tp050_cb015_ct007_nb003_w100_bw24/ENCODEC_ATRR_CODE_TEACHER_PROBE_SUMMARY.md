# Encodec ATRR Code Teacher Probe Summary v1

- rows: `8`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- quantizer_range: `[24, 32)`
- candidate_count: `6`
- avg target_logmel_delta_l1_db: `0.0678`
- avg teacher_projection_rms: `0.0165`
- avg teacher_projection_l1: `0.0094`
- avg nonbase_mass: `0.1152`
- avg base_choice_prob: `0.8848`
- avg teacher_final_mel_loss: `0.004483`
- avg teacher_final_wave_l1: `0.000330`
- avg final_wave_l1: `0.000363`
- avg core_mask_ratio: `0.0609`

## Strongest Teacher-Gap Rows

- `libritts_r__174__174_50561_000024_000000__d665dc2840` | projection_rms=`0.021737` | nonbase=`0.123422`
- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | projection_rms=`0.021216` | nonbase=`0.130833`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | projection_rms=`0.018844` | nonbase=`0.108778`

## Highest Non-Base Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | nonbase=`0.130833` | base_prob=`0.869167`
- `vctk_corpus_0_92__p231__p231_011_mic1__986481509c` | nonbase=`0.127300` | base_prob=`0.872700`
- `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640` | nonbase=`0.123556` | base_prob=`0.876444`
