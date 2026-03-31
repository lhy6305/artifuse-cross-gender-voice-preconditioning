# ATRR Carrier Structure Audit v1

## Scope

- This audit reads machine-probe summary csv files directly.
- It separates carrier-only distortion from target-edit-added distortion.

## Pack Summary

### `v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8`

- rows: `8`
- avg carrier_target_shift_score: `40.84`
- avg target_log_mel_mae: `0.7197`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `58.03`
- avg edit_added_structure_risk: `36.90`
- top target risk records: `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__174__174_50561_000024_000000__d665dc2840;vctk_corpus_0_92__p241__p241_005_mic1__21df46b3a2`

### `v1_fixed8_v9a_bigvgan_11025_anchor075_blend075_pc150_cap200_full8`

- rows: `8`
- avg carrier_target_shift_score: `45.10`
- avg target_log_mel_mae: `0.5693`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `45.76`
- avg edit_added_structure_risk: `24.63`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9`

### `v1_fixed8_v9a_bigvgan_11025_anchor050_blend075_pc150_cap200_full8`

- rows: `8`
- avg carrier_target_shift_score: `39.95`
- avg target_log_mel_mae: `0.4553`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `33.36`
- avg edit_added_structure_risk: `12.22`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;libritts_r__1919__1919_142785_000089_000003__11e66c65d9;libritts_r__2086__2086_149214_000006_000002__23f1c25eb7`
