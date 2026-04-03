# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.26`
- avg core_resonance_coverage_score: `57.65`
- avg over_localized_edit_penalty: `32.01`
- avg context_consistency_score: `55.73`
- avg frame_improvement_mean: `0.001496`

## By Direction

### `feminine`

- avg shift score: `38.77`
- avg core coverage: `52.34`
- avg localization penalty: `27.70`
- avg context consistency: `53.55`
- avg frame improvement mean: `0.001509`

### `masculine`

- avg shift score: `45.75`
- avg core coverage: `62.95`
- avg localization penalty: `36.33`
- avg context consistency: `57.92`
- avg frame improvement mean: `0.001482`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`37.79` | shift=`51.15` | localization_penalty=`24.01`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`38.01` | shift=`51.85` | localization_penalty=`17.06`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`41.13` | shift=`55.19` | localization_penalty=`21.58`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.81` | orig_target_emd=`0.018391` | proc_target_emd=`0.030966`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.44` | orig_target_emd=`0.019670` | proc_target_emd=`0.028545`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.21` | orig_target_emd=`0.017215` | proc_target_emd=`0.023339`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
