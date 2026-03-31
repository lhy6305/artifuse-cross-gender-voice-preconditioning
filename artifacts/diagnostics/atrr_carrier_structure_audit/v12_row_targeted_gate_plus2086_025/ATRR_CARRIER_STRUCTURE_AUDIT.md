# ATRR Carrier Structure Audit v1

## Scope

- This audit reads machine-probe summary csv files directly.
- It separates carrier-only distortion from target-edit-added distortion.

## Pack Summary

### `v1_fixed8_v9a_bigvgan_11025_anchor075_binmask_hybrid_m010_f015_occ005_blend075_pc150_cap200_full8`

- rows: `8`
- avg carrier_target_shift_score: `41.65`
- avg target_log_mel_mae: `0.5445`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `36.40`
- avg edit_added_structure_risk: `15.26`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9`

### `v1_fixed8_v9a_bigvgan_11025_hybrid_rowveto_p230_full8`

- rows: `8`
- avg carrier_target_shift_score: `42.23`
- avg target_log_mel_mae: `0.4472`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `31.21`
- avg edit_added_structure_risk: `10.08`
- top target risk records: `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9;libritts_r__1995__1995_1826_000022_000000__82d5a66723`

### `v1_fixed8_v9a_bigvgan_11025_hybrid_rowveto_p230_rowoverride_2086_020_full8`

- rows: `8`
- avg carrier_target_shift_score: `42.27`
- avg target_log_mel_mae: `0.4482`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `31.18`
- avg edit_added_structure_risk: `10.04`
- top target risk records: `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9;libritts_r__1995__1995_1826_000022_000000__82d5a66723`

### `v1_fixed8_v9a_bigvgan_11025_hybrid_rowveto_p230_rowoverride_2086_025_full8`

- rows: `8`
- avg carrier_target_shift_score: `42.91`
- avg target_log_mel_mae: `0.4446`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `31.01`
- avg edit_added_structure_risk: `9.87`
- top target risk records: `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9;libritts_r__1995__1995_1826_000022_000000__82d5a66723`
