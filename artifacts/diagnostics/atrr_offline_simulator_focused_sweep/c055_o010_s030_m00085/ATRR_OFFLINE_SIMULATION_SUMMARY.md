# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.550`
- off_core_step_size: `0.100`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0085`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `53.99`
- avg sim_core_resonance_coverage_score: `66.50`
- avg sim_over_localized_edit_penalty: `34.63`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.005519`

## By Direction

### `feminine`

- avg shift score: `53.80`
- avg core coverage: `65.12`
- avg localization penalty: `33.56`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.005046`

### `masculine`

- avg shift score: `54.17`
- avg core coverage: `67.88`
- avg localization penalty: `35.70`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.005993`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`55.40` | frame_improvement=`0.003907` | coverage=`56.04`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`54.48` | frame_improvement=`0.003652` | coverage=`56.84`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`54.10` | frame_improvement=`0.007049` | coverage=`65.61`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`52.53` | frame_improvement=`0.004079` | coverage=`77.60`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`53.57` | frame_improvement=`0.005628` | coverage=`71.71`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`53.70` | frame_improvement=`0.006568` | coverage=`55.13`
