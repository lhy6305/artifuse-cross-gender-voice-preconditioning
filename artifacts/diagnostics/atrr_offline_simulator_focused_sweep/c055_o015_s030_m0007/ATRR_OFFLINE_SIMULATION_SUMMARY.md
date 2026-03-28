# ATRR Offline Simulator Summary

## Parameters

- core_step_size: `0.550`
- off_core_step_size: `0.150`
- frame_smoothness_weight: `0.300`
- max_bin_step: `0.0070`

## Pack Summary

- rows: `8`
- avg sim_resonance_distribution_shift_score: `54.73`
- avg sim_core_resonance_coverage_score: `57.61`
- avg sim_over_localized_edit_penalty: `30.10`
- avg sim_context_consistency_score: `99.96`
- avg sim_frame_improvement_mean: `0.006714`

## By Direction

### `feminine`

- avg shift score: `54.22`
- avg core coverage: `55.17`
- avg localization penalty: `28.05`
- avg context consistency: `99.91`
- avg frame improvement mean: `0.006008`

### `masculine`

- avg shift score: `55.24`
- avg core coverage: `60.04`
- avg localization penalty: `32.14`
- avg context consistency: `100.00`
- avg frame improvement mean: `0.007420`

## Strongest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`56.94` | frame_improvement=`0.004818` | coverage=`44.68`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`56.81` | frame_improvement=`0.009220` | coverage=`58.18`
- `stage0_speech_lsf_libritts_masculine_v7` | shift=`56.35` | frame_improvement=`0.009502` | coverage=`68.06`

## Weakest Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`52.72` | frame_improvement=`0.004523` | coverage=`68.82`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`52.81` | frame_improvement=`0.006489` | coverage=`64.61`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`53.48` | frame_improvement=`0.007086` | coverage=`60.71`
