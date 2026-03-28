# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.450`
- off_core_step_size: `0.100`
- frame_smoothness_weight: `0.200`
- max_bin_step: `0.0150`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `55.32`
- avg sim_core_resonance_coverage_score: `74.45`
- avg sim_over_localized_edit_penalty: `38.26`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.007024`

## By Direction

### `feminine`

- avg shift score: `55.41`
- avg core coverage: `73.39`
- avg localization penalty: `37.59`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.006575`

### `masculine`

- avg shift score: `55.23`
- avg core coverage: `75.52`
- avg localization penalty: `38.92`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.007473`

## Strongest Rows

- `stage0_speech_lsf_vctk_masculine_v7` | shift=`57.81` | frame_improvement=`0.008345` | coverage=`77.06`
- `stage0_speech_lsf_vctk_feminine_v7` | shift=`56.71` | frame_improvement=`0.005026` | coverage=`66.01`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`56.07` | frame_improvement=`0.004599` | coverage=`67.30`

## Weakest Rows

- `stage0_speech_lsf_libritts_masculine_v7` | shift=`53.29` | frame_improvement=`0.008455` | coverage=`73.15`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`53.76` | frame_improvement=`0.008494` | coverage=`84.56`
- `stage0_speech_lsf_vctk_feminine_v7` | shift=`54.06` | frame_improvement=`0.005567` | coverage=`85.20`
