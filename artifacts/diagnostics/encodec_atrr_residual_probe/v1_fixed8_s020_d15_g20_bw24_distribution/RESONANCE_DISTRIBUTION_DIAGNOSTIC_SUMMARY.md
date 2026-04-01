# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.38`
- avg core_resonance_coverage_score: `57.62`
- avg over_localized_edit_penalty: `30.43`
- avg context_consistency_score: `51.76`
- avg frame_improvement_mean: `0.000179`

## By Direction

### `feminine`

- avg shift score: `39.86`
- avg core coverage: `54.17`
- avg localization penalty: `25.74`
- avg context consistency: `51.33`
- avg frame improvement mean: `0.001769`

### `masculine`

- avg shift score: `44.91`
- avg core coverage: `61.07`
- avg localization penalty: `35.12`
- avg context consistency: `52.20`
- avg frame improvement mean: `-0.001412`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`40.90` | shift=`49.50` | localization_penalty=`20.78`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`41.59` | shift=`50.57` | localization_penalty=`27.42`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`43.98` | shift=`50.25` | localization_penalty=`21.21`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`18.63` | orig_target_emd=`0.018391` | proc_target_emd=`0.029928`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.58` | orig_target_emd=`0.019670` | proc_target_emd=`0.028489`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`35.15` | orig_target_emd=`0.017215` | proc_target_emd=`0.022329`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
