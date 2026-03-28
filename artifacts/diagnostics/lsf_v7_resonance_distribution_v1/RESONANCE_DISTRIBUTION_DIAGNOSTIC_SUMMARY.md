# Resonance Distribution Diagnostic Summary

- rows: `8`
- avg resonance_distribution_shift_score: `41.70`
- avg core_resonance_coverage_score: `46.40`
- avg over_localized_edit_penalty: `26.20`
- avg context_consistency_score: `46.44`

## By Direction

### `feminine`

- avg shift score: `35.72`
- avg core coverage: `52.68`
- avg localization penalty: `26.78`
- avg context consistency: `44.35`

### `masculine`

- avg shift score: `47.67`
- avg core coverage: `40.12`
- avg localization penalty: `25.62`
- avg context consistency: `48.54`

## Lowest Core Coverage Rows

- `stage0_speech_lsf_vctk_masculine_v7` | coverage=`30.05` | shift=`35.22` | localization_penalty=`26.42`
- `stage0_speech_lsf_libritts_masculine_v7` | coverage=`30.56` | shift=`45.66` | localization_penalty=`21.78`
- `stage0_speech_lsf_libritts_feminine_v7` | coverage=`32.28` | shift=`26.79` | localization_penalty=`17.98`

## Weakest Shift Rows

- `stage0_speech_lsf_vctk_feminine_v7` | shift=`18.44` | orig_target_emd=`0.016941` | proc_target_emd=`0.027633`
- `stage0_speech_lsf_libritts_feminine_v7` | shift=`26.79` | orig_target_emd=`0.033247` | proc_target_emd=`0.048681`
- `stage0_speech_lsf_vctk_masculine_v7` | shift=`35.22` | orig_target_emd=`0.014705` | proc_target_emd=`0.019050`

## Diagnostic Reading

- `resonance_distribution_shift_score` uses a 1D distribution-distance improvement measure toward a same-dataset target-gender prototype.
- `core_resonance_coverage_score` measures how much of the edit lands inside the combined core support of the source and target distributions.
- `over_localized_edit_penalty` is high when the edit mass is too concentrated in a narrow region.
- `context_consistency_score` measures how often frame-level movement toward the target prototype is positive on voiced active frames.
