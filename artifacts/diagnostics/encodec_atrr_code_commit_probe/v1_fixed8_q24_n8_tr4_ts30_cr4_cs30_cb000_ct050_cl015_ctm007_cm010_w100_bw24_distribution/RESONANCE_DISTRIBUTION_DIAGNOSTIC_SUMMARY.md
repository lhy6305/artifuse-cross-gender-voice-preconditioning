# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `40.89`
- avg core_resonance_coverage_score: `58.03`
- avg over_localized_edit_penalty: `32.45`
- avg context_consistency_score: `54.48`
- avg frame_improvement_mean: `-0.000070`

## By Direction

### `feminine`

- avg shift score: `38.35`
- avg core coverage: `53.71`
- avg localization penalty: `28.90`
- avg context consistency: `52.96`
- avg frame improvement mean: `0.001275`

### `masculine`

- avg shift score: `43.42`
- avg core coverage: `62.36`
- avg localization penalty: `36.00`
- avg context consistency: `55.99`
- avg frame improvement mean: `-0.001416`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`37.68` | shift=`51.93` | localization_penalty=`23.75`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`39.94` | shift=`50.94` | localization_penalty=`20.29`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`44.28` | shift=`54.54` | localization_penalty=`21.48`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.60` | orig_target_emd=`0.018391` | proc_target_emd=`0.031042`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`22.59` | orig_target_emd=`0.019670` | proc_target_emd=`0.030454`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.34` | orig_target_emd=`0.017215` | proc_target_emd=`0.023296`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
