# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.90`
- avg core_resonance_coverage_score: `58.61`
- avg over_localized_edit_penalty: `31.25`
- avg context_consistency_score: `51.78`
- avg frame_improvement_mean: `0.000091`

## By Direction

### `feminine`

- avg shift score: `40.73`
- avg core coverage: `56.20`
- avg localization penalty: `27.50`
- avg context consistency: `50.97`
- avg frame improvement mean: `0.001645`

### `masculine`

- avg shift score: `45.07`
- avg core coverage: `61.03`
- avg localization penalty: `35.00`
- avg context consistency: `52.60`
- avg frame improvement mean: `-0.001462`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`36.79` | shift=`49.55` | localization_penalty=`19.26`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`43.85` | shift=`52.16` | localization_penalty=`29.11`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`46.67` | shift=`50.22` | localization_penalty=`22.32`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`17.36` | orig_target_emd=`0.018391` | proc_target_emd=`0.030398`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`25.71` | orig_target_emd=`0.019670` | proc_target_emd=`0.029225`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`41.94` | orig_target_emd=`0.017215` | proc_target_emd=`0.019989`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
