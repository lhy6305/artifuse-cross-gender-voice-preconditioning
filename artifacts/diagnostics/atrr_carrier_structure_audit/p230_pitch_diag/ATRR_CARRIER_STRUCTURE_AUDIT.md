# ATRR Carrier Structure Audit v1

## Scope

- This audit reads machine-probe summary csv files directly.
- It separates carrier-only distortion from target-edit-added distortion.

## Pack Summary

### `p230_anchor075_cap400_single`

- rows: `1`
- avg carrier_target_shift_score: `4.21`
- avg target_log_mel_mae: `1.5001`
- avg source_probe_structure_risk_score: `24.28`
- avg target_probe_structure_risk_score: `64.36`
- avg edit_added_structure_risk: `40.07`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640`

### `p230_anchor075_cap700_single`

- rows: `1`
- avg carrier_target_shift_score: `0.00`
- avg target_log_mel_mae: `2.0918`
- avg source_probe_structure_risk_score: `24.28`
- avg target_probe_structure_risk_score: `64.50`
- avg edit_added_structure_risk: `40.22`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640`

### `p230_anchor075_voicedonly_cap700_single`

- rows: `1`
- avg carrier_target_shift_score: `0.00`
- avg target_log_mel_mae: `0.8956`
- avg source_probe_structure_risk_score: `24.28`
- avg target_probe_structure_risk_score: `61.47`
- avg edit_added_structure_risk: `37.19`
- top target risk records: `vctk_corpus_0_92__p230__p230_107_mic1__8330d16640`
