# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.32`
- avg core_resonance_coverage_score: `57.49`
- avg over_localized_edit_penalty: `32.04`
- avg context_consistency_score: `55.91`
- avg frame_improvement_mean: `0.001699`

## By Direction

### `feminine`

- avg shift score: `38.82`
- avg core coverage: `52.71`
- avg localization penalty: `27.66`
- avg context consistency: `53.90`
- avg frame improvement mean: `0.001538`

### `masculine`

- avg shift score: `45.82`
- avg core coverage: `62.27`
- avg localization penalty: `36.42`
- avg context consistency: `57.92`
- avg frame improvement mean: `0.001860`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`34.87` | shift=`51.17` | localization_penalty=`24.21`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`38.60` | shift=`51.87` | localization_penalty=`17.49`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`42.00` | shift=`55.31` | localization_penalty=`21.08`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.89` | orig_target_emd=`0.018391` | proc_target_emd=`0.030937`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.69` | orig_target_emd=`0.019670` | proc_target_emd=`0.028446`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.20` | orig_target_emd=`0.017215` | proc_target_emd=`0.023345`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
