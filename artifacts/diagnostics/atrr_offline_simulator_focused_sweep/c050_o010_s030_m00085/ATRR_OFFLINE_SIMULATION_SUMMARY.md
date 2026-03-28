# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.500`
- off_core_step_size: `0.100`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0085`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `53.99`
- avg sim_core_resonance_coverage_score: `66.58`
- avg sim_over_localized_edit_penalty: `34.62`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.005513`

## By Direction

### `feminine`

- avg shift score: `53.80`
- avg core coverage: `65.31`
- avg localization penalty: `33.54`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.005036`

### `masculine`

- avg shift score: `54.18`
- avg core coverage: `67.84`
- avg localization penalty: `35.71`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.005990`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`55.40` | frame_improvement=`0.003906` | coverage=`56.05`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`54.47` | frame_improvement=`0.003650` | coverage=`56.79`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`54.10` | frame_improvement=`0.007050` | coverage=`65.62`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`52.54` | frame_improvement=`0.004073` | coverage=`77.66`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`53.56` | frame_improvement=`0.005620` | coverage=`71.76`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`53.69` | frame_improvement=`0.006545` | coverage=`55.79`
