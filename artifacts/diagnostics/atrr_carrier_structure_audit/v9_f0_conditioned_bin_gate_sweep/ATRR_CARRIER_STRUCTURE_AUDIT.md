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

### `v1_fixed8_v9a_bigvgan_11025_hybrid_f0_mmid015_full8`

- rows: `8`
- avg carrier_target_shift_score: `40.59`
- avg target_log_mel_mae: `0.5437`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `35.73`
- avg edit_added_structure_risk: `14.60`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9`

### `v1_fixed8_v9a_bigvgan_11025_hybrid_f0_fhigh020_full8`

- rows: `8`
- avg carrier_target_shift_score: `39.92`
- avg target_log_mel_mae: `0.5459`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `36.31`
- avg edit_added_structure_risk: `15.18`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9`

### `v1_fixed8_v9a_bigvgan_11025_hybrid_f0_mmid015_fhigh020_full8`

- rows: `8`
- avg carrier_target_shift_score: `38.85`
- avg target_log_mel_mae: `0.5451`
- avg source_probe_structure_risk_score: `21.13`
- avg target_probe_structure_risk_score: `35.65`
- avg edit_added_structure_risk: `14.52`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640;libritts_r__2086__2086_149214_000006_000002__23f1c25eb7;libritts_r__1919__1919_142785_000089_000003__11e66c65d9`
