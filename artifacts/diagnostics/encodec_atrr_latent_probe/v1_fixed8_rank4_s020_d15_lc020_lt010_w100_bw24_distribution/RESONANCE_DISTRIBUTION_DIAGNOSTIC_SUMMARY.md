# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.29`
- avg core_resonance_coverage_score: `58.46`
- avg over_localized_edit_penalty: `32.06`
- avg context_consistency_score: `55.76`
- avg frame_improvement_mean: `0.001509`

## By Direction

### `feminine`

- avg shift score: `38.85`
- avg core coverage: `53.74`
- avg localization penalty: `27.95`
- avg context consistency: `53.66`
- avg frame improvement mean: `0.001540`

### `masculine`

- avg shift score: `45.74`
- avg core coverage: `63.18`
- avg localization penalty: `36.18`
- avg context consistency: `57.87`
- avg frame improvement mean: `0.001479`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`38.56` | shift=`51.09` | localization_penalty=`23.33`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`41.82` | shift=`52.05` | localization_penalty=`18.82`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`43.04` | shift=`55.29` | localization_penalty=`20.82`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.87` | orig_target_emd=`0.018391` | proc_target_emd=`0.030946`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`27.46` | orig_target_emd=`0.019670` | proc_target_emd=`0.028537`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.18` | orig_target_emd=`0.017215` | proc_target_emd=`0.023350`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
