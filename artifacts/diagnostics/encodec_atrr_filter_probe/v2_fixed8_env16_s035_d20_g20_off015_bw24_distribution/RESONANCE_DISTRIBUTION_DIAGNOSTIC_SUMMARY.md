# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `37.95`
- avg core_resonance_coverage_score: `55.76`
- avg over_localized_edit_penalty: `28.67`
- avg context_consistency_score: `56.57`
- avg frame_improvement_mean: `-0.002012`

## By Direction

### `feminine`

- avg shift score: `30.87`
- avg core coverage: `50.33`
- avg localization penalty: `24.73`
- avg context consistency: `53.70`
- avg frame improvement mean: `-0.000637`

### `masculine`

- avg shift score: `45.03`
- avg core coverage: `61.19`
- avg localization penalty: `32.60`
- avg context consistency: `59.44`
- avg frame improvement mean: `-0.003388`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`34.27` | shift=`47.64` | localization_penalty=`13.06`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`38.40` | shift=`41.49` | localization_penalty=`15.38`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`41.35` | shift=`54.90` | localization_penalty=`16.26`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`9.36` | orig_target_emd=`0.018391` | proc_target_emd=`0.033340`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`24.98` | orig_target_emd=`0.017215` | proc_target_emd=`0.025831`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`31.03` | orig_target_emd=`0.019670` | proc_target_emd=`0.027132`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
