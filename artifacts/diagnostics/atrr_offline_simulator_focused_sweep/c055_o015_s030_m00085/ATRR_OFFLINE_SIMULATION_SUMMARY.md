# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.550`
- off_core_step_size: `0.150`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0085`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `55.05`
- avg sim_core_resonance_coverage_score: `60.59`
- avg sim_over_localized_edit_penalty: `31.38`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.007113`

## By Direction

### `feminine`

- avg shift score: `54.62`
- avg core coverage: `58.89`
- avg localization penalty: `29.80`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.006413`

### `masculine`

- avg shift score: `55.49`
- avg core coverage: `62.29`
- avg localization penalty: `32.97`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.007813`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`57.22` | frame_improvement=`0.005084` | coverage=`48.24`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`56.60` | frame_improvement=`0.009540` | coverage=`60.44`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`56.23` | frame_improvement=`0.009805` | coverage=`71.20`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`53.01` | frame_improvement=`0.004929` | coverage=`71.76`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`53.65` | frame_improvement=`0.007162` | coverage=`66.43`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`53.99` | frame_improvement=`0.007444` | coverage=`64.82`
