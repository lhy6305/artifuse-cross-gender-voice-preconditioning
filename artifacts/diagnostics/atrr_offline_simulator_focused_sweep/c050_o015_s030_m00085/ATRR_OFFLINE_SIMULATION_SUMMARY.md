# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.500`
- off_core_step_size: `0.150`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0085`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `55.05`
- avg sim_core_resonance_coverage_score: `60.67`
- avg sim_over_localized_edit_penalty: `31.39`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.007107`

## By Direction

### `feminine`

- avg shift score: `54.61`
- avg core coverage: `59.08`
- avg localization penalty: `29.79`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.006404`

### `masculine`

- avg shift score: `55.49`
- avg core coverage: `62.25`
- avg localization penalty: `32.99`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.007810`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`57.22` | frame_improvement=`0.005083` | coverage=`48.26`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`56.60` | frame_improvement=`0.009541` | coverage=`60.44`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`56.23` | frame_improvement=`0.009805` | coverage=`71.19`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`53.02` | frame_improvement=`0.004923` | coverage=`71.80`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`53.67` | frame_improvement=`0.007151` | coverage=`66.35`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`53.98` | frame_improvement=`0.007436` | coverage=`64.87`
