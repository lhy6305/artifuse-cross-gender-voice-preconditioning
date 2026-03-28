# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.500`
- off_core_step_size: `0.100`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0100`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `54.29`
- avg sim_core_resonance_coverage_score: `68.99`
- avg sim_over_localized_edit_penalty: `35.79`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.005862`

## By Direction

### `feminine`

- avg shift score: `54.16`
- avg core coverage: `67.83`
- avg localization penalty: `34.82`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.005392`

### `masculine`

- avg shift score: `54.42`
- avg core coverage: `70.15`
- avg localization penalty: `36.77`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.006332`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`55.70` | frame_improvement=`0.004160` | coverage=`59.15`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`54.92` | frame_improvement=`0.006626` | coverage=`72.55`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`54.87` | frame_improvement=`0.003872` | coverage=`60.02`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`52.84` | frame_improvement=`0.004447` | coverage=`79.89`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`53.91` | frame_improvement=`0.007353` | coverage=`68.07`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`54.00` | frame_improvement=`0.007475` | coverage=`79.95`
