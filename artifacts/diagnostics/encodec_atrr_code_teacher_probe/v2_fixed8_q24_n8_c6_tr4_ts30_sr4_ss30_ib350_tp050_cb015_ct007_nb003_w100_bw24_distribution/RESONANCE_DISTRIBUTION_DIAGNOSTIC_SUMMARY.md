# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.26`
- avg core_resonance_coverage_score: `57.91`
- avg over_localized_edit_penalty: `32.47`
- avg context_consistency_score: `55.64`
- avg frame_improvement_mean: `0.001503`

## By Direction

### `feminine`

- avg shift score: `38.58`
- avg core coverage: `52.99`
- avg localization penalty: `28.33`
- avg context consistency: `53.31`
- avg frame improvement mean: `0.001254`

### `masculine`

- avg shift score: `45.95`
- avg core coverage: `62.83`
- avg localization penalty: `36.61`
- avg context consistency: `57.98`
- avg frame improvement mean: `0.001752`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`37.28` | shift=`51.95` | localization_penalty=`24.11`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`38.86` | shift=`51.57` | localization_penalty=`19.55`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`43.75` | shift=`54.59` | localization_penalty=`21.32`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.46` | orig_target_emd=`0.018391` | proc_target_emd=`0.031094`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.45` | orig_target_emd=`0.019670` | proc_target_emd=`0.028540`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.68` | orig_target_emd=`0.017215` | proc_target_emd=`0.023179`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
