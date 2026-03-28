# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.550`
- off_core_step_size: `0.100`
- frame_smoothness_weight: `0.250`
- max_bin_step: `0.0150`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `55.30`
- avg sim_core_resonance_coverage_score: `74.24`
- avg sim_over_localized_edit_penalty: `38.32`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.007017`

## By Direction

### `feminine`

- avg shift score: `55.38`
- avg core coverage: `73.01`
- avg localization penalty: `37.62`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.006579`

### `masculine`

- avg shift score: `55.22`
- avg core coverage: `75.48`
- avg localization penalty: `39.01`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.007455`

## Strongest Rows

- `stage0_speech_lsf_vctk_masculine_v7` | shift=`57.71` | frame_improvement=`0.008426` | coverage=`76.67`
- `stage0_speech_lsf_vctk_feminine_v7` | shift=`56.72` | frame_improvement=`0.005015` | coverage=`66.01`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`56.12` | frame_improvement=`0.004589` | coverage=`67.40`

## Weakest Rows

- `stage0_speech_lsf_libritts_masculine_v7` | shift=`53.30` | frame_improvement=`0.008381` | coverage=`73.20`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`53.76` | frame_improvement=`0.008425` | coverage=`84.65`
- `stage0_speech_lsf_vctk_feminine_v7` | shift=`53.91` | frame_improvement=`0.005643` | coverage=`84.76`
