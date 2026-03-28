# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.550`
- off_core_step_size: `0.100`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0070`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `53.68`
- avg sim_core_resonance_coverage_score: `63.51`
- avg sim_over_localized_edit_penalty: `32.94`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.005150`

## By Direction

### `feminine`

- avg shift score: `53.43`
- avg core coverage: `61.85`
- avg localization penalty: `31.71`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.004670`

### `masculine`

- avg shift score: `53.93`
- avg core coverage: `65.18`
- avg localization penalty: `34.17`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.005629`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`55.10` | frame_improvement=`0.003650` | coverage=`52.23`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`54.30` | frame_improvement=`0.006736` | coverage=`62.85`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`54.16` | frame_improvement=`0.006912` | coverage=`74.71`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`52.24` | frame_improvement=`0.003686` | coverage=`74.78`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`53.11` | frame_improvement=`0.005304` | coverage=`68.55`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`53.21` | frame_improvement=`0.005446` | coverage=`69.16`
