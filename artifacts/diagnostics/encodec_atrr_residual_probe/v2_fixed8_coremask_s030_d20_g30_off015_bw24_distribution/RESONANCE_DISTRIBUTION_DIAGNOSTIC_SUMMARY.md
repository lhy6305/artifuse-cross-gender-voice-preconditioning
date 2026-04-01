# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.42`
- avg core_resonance_coverage_score: `59.07`
- avg over_localized_edit_penalty: `31.78`
- avg context_consistency_score: `47.58`
- avg frame_improvement_mean: `-0.000358`

## By Direction

### `feminine`

- avg shift score: `39.84`
- avg core coverage: `57.21`
- avg localization penalty: `28.14`
- avg context consistency: `48.41`
- avg frame improvement mean: `0.001167`

### `masculine`

- avg shift score: `45.00`
- avg core coverage: `60.94`
- avg localization penalty: `35.42`
- avg context consistency: `46.75`
- avg frame improvement mean: `-0.001883`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`35.16` | shift=`49.44` | localization_penalty=`18.86`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`45.31` | shift=`52.04` | localization_penalty=`30.01`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`48.37` | shift=`49.60` | localization_penalty=`22.94`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`17.28` | orig_target_emd=`0.018391` | proc_target_emd=`0.030426`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`25.88` | orig_target_emd=`0.019670` | proc_target_emd=`0.029159`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`41.37` | orig_target_emd=`0.017215` | proc_target_emd=`0.020185`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
