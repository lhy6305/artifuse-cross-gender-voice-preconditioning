# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.550`
- off_core_step_size: `0.150`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0100`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `55.36`
- avg sim_core_resonance_coverage_score: `63.06`
- avg sim_over_localized_edit_penalty: `32.59`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.007485`

## By Direction

### `feminine`

- avg shift score: `54.99`
- avg core coverage: `61.78`
- avg localization penalty: `31.24`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.006797`

### `masculine`

- avg shift score: `55.73`
- avg core coverage: `64.34`
- avg localization penalty: `33.93`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.008173`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`57.50` | frame_improvement=`0.005342` | coverage=`51.32`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`56.40` | frame_improvement=`0.009854` | coverage=`62.17`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`56.12` | frame_improvement=`0.010094` | coverage=`73.88`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`53.30` | frame_improvement=`0.005317` | coverage=`74.24`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`54.47` | frame_improvement=`0.007785` | coverage=`67.84`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`54.53` | frame_improvement=`0.007767` | coverage=`68.26`
