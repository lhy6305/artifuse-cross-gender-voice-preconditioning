# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `41.94`
- avg core_resonance_coverage_score: `57.57`
- avg over_localized_edit_penalty: `31.52`
- avg context_consistency_score: `57.10`
- avg frame_improvement_mean: `0.001742`

## By Direction

### `feminine`

- avg shift score: `38.08`
- avg core coverage: `51.60`
- avg localization penalty: `27.80`
- avg context consistency: `54.59`
- avg frame improvement mean: `0.001582`

### `masculine`

- avg shift score: `45.79`
- avg core coverage: `63.54`
- avg localization penalty: `35.23`
- avg context consistency: `59.61`
- avg frame improvement mean: `0.001903`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`36.60` | shift=`50.18` | localization_penalty=`22.03`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`36.95` | shift=`50.65` | localization_penalty=`16.92`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`38.80` | shift=`53.67` | localization_penalty=`21.28`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.38` | orig_target_emd=`0.018391` | proc_target_emd=`0.031125`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.58` | orig_target_emd=`0.019670` | proc_target_emd=`0.028492`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.62` | orig_target_emd=`0.017215` | proc_target_emd=`0.023201`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
