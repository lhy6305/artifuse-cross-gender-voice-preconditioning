# Encodec ATRR Code Gate Probe Summary v1

- rows: `8`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- quantizer_range: `[24, 32)`
- avg target_logmel_delta_l1_db: `0.0678`
- avg teacher_code_gap_rms: `0.0417`
- avg teacher_code_gap_l1: `0.0176`
- avg gate_mean: `0.1011`
- avg base_keep_mean: `0.8989`
- avg teacher_final_mel_loss: `0.004482`
- avg teacher_final_wave_l1: `0.000326`
- avg final_wave_l1: `0.000064`
- avg core_mask_ratio: `0.0609`

## Largest Teacher-Code Gap Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | gap_rms=`0.046841` | gate_mean=`0.109007`
- `vctk_corpus_0_92__p226__p226_011_mic1__8ef2d6c73f` | gap_rms=`0.044872` | gate_mean=`0.090711`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | gap_rms=`0.042907` | gate_mean=`0.101739`

## Highest Gate Rows

- `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640` | gate_mean=`0.109406` | base_keep=`0.890594`
- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | gate_mean=`0.109007` | base_keep=`0.890993`
- `vctk_corpus_0_92__p231__p231_011_mic1__986481509c` | gate_mean=`0.105810` | base_keep=`0.894190`
