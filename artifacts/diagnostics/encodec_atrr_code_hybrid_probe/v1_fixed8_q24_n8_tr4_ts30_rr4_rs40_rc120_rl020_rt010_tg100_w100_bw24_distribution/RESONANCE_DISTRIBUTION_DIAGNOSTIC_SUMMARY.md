# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `41.58`
- avg core_resonance_coverage_score: `57.14`
- avg over_localized_edit_penalty: `31.61`
- avg context_consistency_score: `55.17`
- avg frame_improvement_mean: `0.000962`

## By Direction

### `feminine`

- avg shift score: `38.58`
- avg core coverage: `53.17`
- avg localization penalty: `27.70`
- avg context consistency: `54.34`
- avg frame improvement mean: `0.001515`

### `masculine`

- avg shift score: `44.57`
- avg core coverage: `61.11`
- avg localization penalty: `35.53`
- avg context consistency: `55.99`
- avg frame improvement mean: `0.000409`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`33.72` | shift=`51.64` | localization_penalty=`22.41`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`38.92` | shift=`51.96` | localization_penalty=`17.63`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`43.59` | shift=`54.33` | localization_penalty=`20.84`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.96` | orig_target_emd=`0.018391` | proc_target_emd=`0.030913`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.61` | orig_target_emd=`0.019670` | proc_target_emd=`0.028477`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.08` | orig_target_emd=`0.017215` | proc_target_emd=`0.023385`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
