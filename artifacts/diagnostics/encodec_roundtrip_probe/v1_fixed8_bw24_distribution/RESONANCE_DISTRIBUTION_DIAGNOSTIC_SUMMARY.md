# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `42.08`
- avg core_resonance_coverage_score: `58.31`
- avg over_localized_edit_penalty: `32.67`
- avg context_consistency_score: `54.68`
- avg frame_improvement_mean: `0.001171`

## By Direction

### `feminine`

- avg shift score: `38.27`
- avg core coverage: `53.83`
- avg localization penalty: `28.81`
- avg context consistency: `52.73`
- avg frame improvement mean: `0.001216`

### `masculine`

- avg shift score: `45.88`
- avg core coverage: `62.80`
- avg localization penalty: `36.53`
- avg context consistency: `56.64`
- avg frame improvement mean: `0.001126`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_libritts_masculine_v8__mid_f0_split_core_focus_v9a` | coverage=`36.74` | shift=`51.35` | localization_penalty=`24.11`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`40.16` | shift=`50.88` | localization_penalty=`20.02`
- `stage0_speech_lsf_libritts_feminine_v8__high_f0_split_core_focus_v9a` | coverage=`44.33` | shift=`54.54` | localization_penalty=`21.42`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v8__high_f0_split_core_focus_v9a` | shift=`15.41` | orig_target_emd=`0.018391` | proc_target_emd=`0.031112`
- `stage0_speech_lsf_vctk_masculine_v8__low_f0_split_core_focus_v9a` | shift=`28.21` | orig_target_emd=`0.019670` | proc_target_emd=`0.028244`
- `stage0_speech_lsf_vctk_feminine_v8__mid_f0_split_core_focus_v9a` | shift=`32.26` | orig_target_emd=`0.017215` | proc_target_emd=`0.023323`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a weighted target-gender prototype conditioned by F0 proximity and distribution similarity.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of source and target energy distributions plus persistent occupancy support.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
