# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.550`
- off_core_step_size: `0.100`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0100`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `54.29`
- avg sim_core_resonance_coverage_score: `68.91`
- avg sim_over_localized_edit_penalty: `35.75`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.005874`

## By Direction

### `feminine`

- avg shift score: `54.16`
- avg core coverage: `67.61`
- avg localization penalty: `34.83`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.005406`

### `masculine`

- avg shift score: `54.41`
- avg core coverage: `70.20`
- avg localization penalty: `36.67`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.006343`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`55.70` | frame_improvement=`0.004162` | coverage=`59.13`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`54.88` | frame_improvement=`0.003875` | coverage=`60.06`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`54.87` | frame_improvement=`0.006666` | coverage=`72.75`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`52.82` | frame_improvement=`0.004458` | coverage=`79.81`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`53.91` | frame_improvement=`0.007353` | coverage=`68.06`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`54.00` | frame_improvement=`0.007476` | coverage=`79.95`
