# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.40`
- avg core_resonance_coverage_score: `58.23`
- avg over_localized_edit_penalty: `31.45`
- avg context_consistency_score: `59.64`
- avg frame_improvement_mean: `0.001752`

## By Direction

### `feminine`

- avg shift score: `38.57`
- avg core coverage: `52.48`
- avg localization penalty: `27.27`
- avg context consistency: `56.63`
- avg frame improvement mean: `0.001863`

### `masculine`

- avg shift score: `46.23`
- avg core coverage: `63.97`
- avg localization penalty: `35.63`
- avg context consistency: `62.64`
- avg frame improvement mean: `0.001642`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`35.82` | shift=`51.91` | localization_penalty=`15.89`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`40.95` | shift=`52.60` | localization_penalty=`21.57`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`43.86` | shift=`53.91` | localization_penalty=`20.94`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.34` | orig_target_emd=`0.018391` | proc_target_emd=`0.031140`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`26.91` | orig_target_emd=`0.019670` | proc_target_emd=`0.028753`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`33.12` | orig_target_emd=`0.017215` | proc_target_emd=`0.023026`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
