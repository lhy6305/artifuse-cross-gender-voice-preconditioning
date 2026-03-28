# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.500`
- off_core_step_size: `0.100`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0070`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `53.68`
- avg sim_core_resonance_coverage_score: `63.59`
- avg sim_over_localized_edit_penalty: `32.96`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.005145`

## By Direction

### `feminine`

- avg shift score: `53.43`
- avg core coverage: `62.03`
- avg localization penalty: `31.74`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.004662`

### `masculine`

- avg shift score: `53.94`
- avg core coverage: `65.16`
- avg localization penalty: `34.17`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.005627`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`55.11` | frame_improvement=`0.003649` | coverage=`52.24`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`54.30` | frame_improvement=`0.006736` | coverage=`62.85`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`54.16` | frame_improvement=`0.006911` | coverage=`74.71`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`52.25` | frame_improvement=`0.003684` | coverage=`74.80`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`53.10` | frame_improvement=`0.005296` | coverage=`68.62`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`53.22` | frame_improvement=`0.005441` | coverage=`69.12`
