# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.13`
- avg core_resonance_coverage_score: `58.23`
- avg over_localized_edit_penalty: `31.89`
- avg context_consistency_score: `55.92`
- avg frame_improvement_mean: `0.001710`

## By Direction

### `feminine`

- avg shift score: `38.63`
- avg core coverage: `52.91`
- avg localization penalty: `27.58`
- avg context consistency: `53.99`
- avg frame improvement mean: `0.001565`

### `masculine`

- avg shift score: `45.63`
- avg core coverage: `63.55`
- avg localization penalty: `36.20`
- avg context consistency: `57.85`
- avg frame improvement mean: `0.001854`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`38.88` | shift=`51.97` | localization_penalty=`17.72`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`40.00` | shift=`50.44` | localization_penalty=`23.42`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`42.67` | shift=`54.39` | localization_penalty=`20.45`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.94` | orig_target_emd=`0.018391` | proc_target_emd=`0.030920`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.69` | orig_target_emd=`0.019670` | proc_target_emd=`0.028447`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.21` | orig_target_emd=`0.017215` | proc_target_emd=`0.023342`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
