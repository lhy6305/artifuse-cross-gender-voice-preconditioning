# Encodec ATRR Code Probe Summary v1

- rows: `8`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- quantizer_range: `[24, 32)`
- neighbor_count: `4`
- avg target_logmel_delta_l1_db: `0.0678`
- avg code_delta_rms: `0.0008`
- avg nonbase_mass: `0.0162`
- avg base_choice_prob: `0.9838`
- avg final_mel_loss: `0.011441`
- avg final_wave_l1: `0.000053`
- avg core_mask_ratio: `0.0609`

## Strongest Code Rows

- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | code_rms=`0.001075` | nonbase=`0.019476`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | code_rms=`0.001060` | nonbase=`0.019140`
- `libritts_r__174__174_50561_000024_000000__d665dc2840` | code_rms=`0.000842` | nonbase=`0.014994`

## Most Conservative Rows

- `vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2` | nonbase=`0.012573` | base_prob=`0.987427`
- `vctk_corpus_0_92__p226__p226_011_mic1__8ef2d6c73f` | nonbase=`0.012649` | base_prob=`0.987351`
- `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7` | nonbase=`0.013758` | base_prob=`0.986242`
