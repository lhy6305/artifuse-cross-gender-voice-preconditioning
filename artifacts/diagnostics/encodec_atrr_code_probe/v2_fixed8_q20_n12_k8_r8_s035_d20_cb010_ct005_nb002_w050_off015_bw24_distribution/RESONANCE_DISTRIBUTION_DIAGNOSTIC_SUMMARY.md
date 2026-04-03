# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.10`
- avg core_resonance_coverage_score: `58.00`
- avg over_localized_edit_penalty: `32.09`
- avg context_consistency_score: `55.80`
- avg frame_improvement_mean: `0.001373`

## By Direction

### `feminine`

- avg shift score: `38.46`
- avg core coverage: `53.38`
- avg localization penalty: `27.87`
- avg context consistency: `53.35`
- avg frame improvement mean: `0.001351`

### `masculine`

- avg shift score: `45.75`
- avg core coverage: `62.62`
- avg localization penalty: `36.30`
- avg context consistency: `58.25`
- avg frame improvement mean: `0.001394`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`36.54` | shift=`51.34` | localization_penalty=`23.79`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`38.94` | shift=`51.71` | localization_penalty=`18.31`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`44.85` | shift=`53.72` | localization_penalty=`21.10`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.82` | orig_target_emd=`0.018391` | proc_target_emd=`0.030962`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.20` | orig_target_emd=`0.019670` | proc_target_emd=`0.028639`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.58` | orig_target_emd=`0.017215` | proc_target_emd=`0.023213`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
