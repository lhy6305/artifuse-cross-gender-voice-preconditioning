# Encodec ATRR Code Commit Probe Summary v1

- rows: `8`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- quantizer_range: `[24, 32)`
- avg target_logmel_delta_l1_db: `0.0678`
- avg teacher_code_gap_rms: `0.0453`
- avg teacher_code_gap_l1: `0.0186`
- avg commit_mean: `0.1477`
- avg base_keep_mean: `0.8523`
- avg teacher_final_mel_loss: `0.004480`
- avg teacher_final_wave_l1: `0.000343`
- avg final_wave_l1: `0.000309`
- avg core_mask_ratio: `0.0609`

## Largest Teacher-Code Gap Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | gap_rms=`0.052317` | commit_mean=`0.229232`
- `vctk_corpus_0_92__p226__p226_011_mic1__8ef2d6c73f` | gap_rms=`0.047721` | commit_mean=`0.070000`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | gap_rms=`0.047372` | commit_mean=`0.147826`

## Highest Commit Rows

- `libritts_r__174__174_50561_000024_000000__d665dc2840` | commit_mean=`0.366935` | base_keep=`0.633065`
- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | commit_mean=`0.229232` | base_keep=`0.770768`
- `vctk_corpus_0_92__p231__p231_011_mic1__986481509c` | commit_mean=`0.185644` | base_keep=`0.814356`
