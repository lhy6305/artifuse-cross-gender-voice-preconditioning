# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.35`
- avg core_resonance_coverage_score: `58.12`
- avg over_localized_edit_penalty: `32.24`
- avg context_consistency_score: `55.71`
- avg frame_improvement_mean: `0.001539`

## By Direction

### `feminine`

- avg shift score: `38.63`
- avg core coverage: `52.79`
- avg localization penalty: `28.29`
- avg context consistency: `53.79`
- avg frame improvement mean: `0.001360`

### `masculine`

- avg shift score: `46.08`
- avg core coverage: `63.45`
- avg localization penalty: `36.19`
- avg context consistency: `57.62`
- avg frame improvement mean: `0.001718`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`39.01` | shift=`51.57` | localization_penalty=`19.86`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`39.75` | shift=`52.48` | localization_penalty=`22.53`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`43.11` | shift=`54.65` | localization_penalty=`21.23`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.65` | orig_target_emd=`0.018391` | proc_target_emd=`0.031024`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.40` | orig_target_emd=`0.019670` | proc_target_emd=`0.028560`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.64` | orig_target_emd=`0.017215` | proc_target_emd=`0.023192`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
