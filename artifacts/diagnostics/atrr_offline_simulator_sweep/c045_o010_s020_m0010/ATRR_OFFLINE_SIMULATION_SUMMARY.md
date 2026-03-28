# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.450`
- off_core_step_size: `0.100`
- frame_smoothness_weight: `0.200`
- max_bin_step: `0.0100`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `54.32`
- avg sim_core_resonance_coverage_score: `69.09`
- avg sim_over_localized_edit_penalty: `35.73`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.005952`

## By Direction

### `feminine`

- avg shift score: `54.19`
- avg core coverage: `68.09`
- avg localization penalty: `34.80`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.005480`

### `masculine`

- avg shift score: `54.44`
- avg core coverage: `70.09`
- avg localization penalty: `36.66`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.006423`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`55.71` | frame_improvement=`0.004185` | coverage=`59.16`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`55.05` | frame_improvement=`0.006670` | coverage=`72.63`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`54.85` | frame_improvement=`0.003907` | coverage=`59.92`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`52.90` | frame_improvement=`0.004506` | coverage=`79.95`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`53.88` | frame_improvement=`0.007497` | coverage=`67.94`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`53.99` | frame_improvement=`0.007619` | coverage=`79.86`
