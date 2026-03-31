# ATRR Carrier Structure Audit v1

## Scope

- This audit reads machine-probe summary csv files directly.
- It separates carrier-only distortion from target-edit-added distortion.

## Pack Summary

### `v1_fixed8_v9a_bigvgan_11025_anchor075_blend075_pc150_cap200_full8`

- rows: `8`
- avg carrier_target_shift_score: `45.10`
- avg target_log_mel_mae: `0.5693`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `45.76`
- avg edit_added_structure_risk: `24.63`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9`

### `v1_fixed8_v9a_bigvgan_11025_anchor075_binmask015_occ005_blend075_pc150_cap200_full8`

- rows: `8`
- avg carrier_target_shift_score: `39.73`
- avg target_log_mel_mae: `0.5442`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `35.61`
- avg edit_added_structure_risk: `14.48`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9`

### `v1_fixed8_v9a_bigvgan_11025_anchor075_binmask020_occ005_blend075_pc150_cap200_full8`

- rows: `8`
- avg carrier_target_shift_score: `38.15`
- avg target_log_mel_mae: `0.5460`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `35.45`
- avg edit_added_structure_risk: `14.32`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9`
