# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `41.88`
- avg core_resonance_coverage_score: `57.35`
- avg over_localized_edit_penalty: `31.83`
- avg context_consistency_score: `55.28`
- avg frame_improvement_mean: `0.001479`

## By Direction

### `feminine`

- avg shift score: `37.83`
- avg core coverage: `52.05`
- avg localization penalty: `27.24`
- avg context consistency: `52.55`
- avg frame improvement mean: `0.001252`

### `masculine`

- avg shift score: `45.94`
- avg core coverage: `62.65`
- avg localization penalty: `36.42`
- avg context consistency: `58.00`
- avg frame improvement mean: `0.001705`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`32.47` | shift=`51.37` | localization_penalty=`14.59`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`36.65` | shift=`51.90` | localization_penalty=`23.49`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`45.39` | shift=`51.90` | localization_penalty=`21.87`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.49` | orig_target_emd=`0.018391` | proc_target_emd=`0.031085`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.31` | orig_target_emd=`0.019670` | proc_target_emd=`0.028595`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.55` | orig_target_emd=`0.017215` | proc_target_emd=`0.023223`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
