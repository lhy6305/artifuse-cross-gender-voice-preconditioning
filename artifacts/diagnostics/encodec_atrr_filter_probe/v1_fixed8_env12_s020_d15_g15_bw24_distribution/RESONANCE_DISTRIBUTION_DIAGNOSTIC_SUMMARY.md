# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `39.42`
- avg core_resonance_coverage_score: `56.81`
- avg over_localized_edit_penalty: `30.29`
- avg context_consistency_score: `56.34`
- avg frame_improvement_mean: `-0.001664`

## By Direction

### `feminine`

- avg shift score: `32.98`
- avg core coverage: `51.95`
- avg localization penalty: `26.68`
- avg context consistency: `54.37`
- avg frame improvement mean: `-0.000846`

### `masculine`

- avg shift score: `45.85`
- avg core coverage: `61.68`
- avg localization penalty: `33.89`
- avg context consistency: `58.32`
- avg frame improvement mean: `-0.002483`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`35.01` | shift=`48.88` | localization_penalty=`16.46`
- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`39.95` | shift=`54.50` | localization_penalty=`18.50`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`44.29` | shift=`47.18` | localization_penalty=`19.76`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`8.41` | orig_target_emd=`0.018391` | proc_target_emd=`0.033687`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`27.45` | orig_target_emd=`0.017215` | proc_target_emd=`0.024981`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`33.47` | orig_target_emd=`0.019670` | proc_target_emd=`0.026174`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
