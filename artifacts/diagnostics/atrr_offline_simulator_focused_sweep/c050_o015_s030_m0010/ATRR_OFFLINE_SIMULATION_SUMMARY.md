# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.500`
- off_core_step_size: `0.150`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0100`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `55.38`
- avg sim_core_resonance_coverage_score: `63.14`
- avg sim_over_localized_edit_penalty: `32.60`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.007472`

## By Direction

### `feminine`

- avg shift score: `55.00`
- avg core coverage: `61.98`
- avg localization penalty: `31.23`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.006784`

### `masculine`

- avg shift score: `55.75`
- avg core coverage: `64.30`
- avg localization penalty: `33.97`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.008162`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`57.51` | frame_improvement=`0.005340` | coverage=`51.33`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`56.40` | frame_improvement=`0.009854` | coverage=`62.18`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`56.12` | frame_improvement=`0.010092` | coverage=`73.87`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`53.32` | frame_improvement=`0.005307` | coverage=`74.29`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`54.47` | frame_improvement=`0.007777` | coverage=`67.87`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`54.60` | frame_improvement=`0.007727` | coverage=`68.12`
