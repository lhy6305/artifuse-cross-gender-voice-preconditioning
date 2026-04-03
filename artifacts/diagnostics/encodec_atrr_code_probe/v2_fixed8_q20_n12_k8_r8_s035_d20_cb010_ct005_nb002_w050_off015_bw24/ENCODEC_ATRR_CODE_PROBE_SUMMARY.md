# Encodec ATRR Code Probe Summary v1

- rows: `8`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- quantizer_range: `[20, 32)`
- neighbor_count: `8`
- avg target_logmel_delta_l1_db: `0.0945`
- avg code_delta_rms: `0.0082`
- avg nonbase_mass: `0.1137`
- avg base_choice_prob: `0.8863`
- avg final_mel_loss: `0.028646`
- avg final_wave_l1: `0.000625`
- avg core_mask_ratio: `0.0609`

## Strongest Code Rows

- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | code_rms=`0.010816` | nonbase=`0.120228`
- `libritts_r__174__174_50561_000024_000000__d665dc2840` | code_rms=`0.009522` | nonbase=`0.111036`
- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | code_rms=`0.008572` | nonbase=`0.099718`

## Most Conservative Rows

- `vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2` | nonbase=`0.097018` | base_prob=`0.902983`
- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | nonbase=`0.099718` | base_prob=`0.900282`
- `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7` | nonbase=`0.107681` | base_prob=`0.892319`
