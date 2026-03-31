# BigVGAN Structure First Anchor Sweep v1

## Summary

This checkpoint records the first structure-first narrow sweep after the first
ATRR BigVGAN human rejection.

Two changes were made:

1. a direct structure audit for carrier summary csv outputs
2. a new pre-vocoder source-anchoring control at the frame-distribution stage

The main result is that the active problem is now better localized:

- the base BigVGAN carrier still adds some distortion
- but the larger structural jump happens when the ATRR edit is injected into the
  carrier input

The best pack-level tradeoff in this sweep is:

- `frame_distribution_anchor_alpha = 0.75`
- `voiced_target_blend_alpha = 0.75`
- post-vocoder pitch correction trigger `150` cents and cap `200` cents

This new stack is better than the previously reviewed BigVGAN stack on both
targetward movement and structure metrics.

But it is still not clean enough for another human pass yet.

## New Tooling

Two scripts are now part of the active route tooling:

- `scripts/audit_speech_structure_from_queue.py`
- `scripts/audit_atrr_vocoder_carrier_summary.py`

The new summary-audit path reads machine-probe summary csv files directly and
separates:

- carrier-only structure distortion from `original -> source_probe`
- edit-added structure distortion from `original -> target_probe`

This avoids sending another carrier candidate to human review before the route
knows whether the structural damage comes mostly from the carrier itself or from
the edit injection step.

## Baseline Split Reading

Baseline stack under this split audit:

- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8/`

Split-audit output:

- `artifacts/diagnostics/atrr_carrier_structure_audit/v1_baseline_split/`

Average reading:

- source probe structure risk: `21.13`
- target probe structure risk: `58.03`
- edit-added structure risk: `36.90`

Interpretation:

- the base carrier is not clean enough yet
- but the dominant route blocker is the edit-added jump after the ATRR target
  package is injected into the carrier input

So the next useful control had to be stronger source anchoring before the
vocoder, not another human review or another backend search.

## New Carrier Control

`scripts/run_atrr_vocoder_carrier_adapter.py` now supports:

- `--frame-distribution-anchor-alpha`

This blends each voiced edited frame distribution with the source frame
distribution before backend-domain target mel is synthesized.

This is different from the older voiced log-mel blend:

- old control blended source and target after backend-domain mel rebuild
- new control anchors the edit earlier, at the frame-distribution stage

## Narrow Sweep

All runs used the same fixed8 target package set and the same BigVGAN backend:

- `external_models/bigvgan_v2_22khz_80band_256x/`

Shared settings:

- `voiced_target_blend_alpha = 0.75`
- `match_source_rms = True`
- pitch correction trigger `150`
- pitch correction cap `200`

Variants:

1. baseline: `frame_distribution_anchor_alpha = 1.00`
2. anchor075: `frame_distribution_anchor_alpha = 0.75`
3. anchor0625: `frame_distribution_anchor_alpha = 0.625`
4. anchor050: `frame_distribution_anchor_alpha = 0.50`

Outputs:

- `artifacts/diagnostics/atrr_carrier_structure_audit/v3_anchor_sweep_plus0625/`

## Pack Level Result

Baseline:

- shift: `40.84`
- target log-mel MAE: `0.7197`
- target probe structure risk: `58.03`
- edit-added structure risk: `36.90`

Anchor075:

- shift: `45.10`
- target log-mel MAE: `0.5693`
- target probe structure risk: `45.76`
- edit-added structure risk: `24.63`

Anchor0625:

- shift: `36.70`
- target log-mel MAE: `0.5131`
- target probe structure risk: `40.01`
- edit-added structure risk: `18.88`

Anchor050:

- shift: `39.95`
- target log-mel MAE: `0.4553`
- target probe structure risk: `33.36`
- edit-added structure risk: `12.22`

Pack-level reading:

- `anchor075` is the best overall tradeoff in this sweep
- `anchor050` is the cleanest structurally at the pack level
- but stronger source anchoring is not monotonic and can still collapse key rows

## Important Row Level Reading

The pack averages hide a critical row-level instability.

For `p241_005_mic1`:

- baseline shift: `34.70`
- anchor075 shift: `28.49`
- anchor0625 shift: `0.00`
- anchor050 shift: `8.07`

So stronger anchoring can improve average structure while destroying a row that
was previously rescued.

The other persistent row-level outlier is `p230_107_mic1`, which remains weak
and structurally risky across the anchor sweep.

This means the route should not treat lower pack-level structure risk as
automatic progress unless row-level targetward movement is also preserved.

## Route Decision

- Keep the ATRR target package family open.
- Keep the first human-reviewed BigVGAN stack rejected.
- Replace that old machine stack with `anchor075` as the new active machine-only
  BigVGAN baseline.
- Do not send `anchor075` to human review yet.

Reason:

- it materially improves both target-shift and structure metrics versus the
  previously reviewed stack
- but the target probe structure risk is still too high for another listening
  pass after the last all-artifact human result

## Immediate Next Step

The next step should stay structure first and row aware:

1. keep `anchor075` as the active pack-level baseline
2. target `p230_107_mic1` and the remaining high-risk rows with a more selective
   source-aware stabilization shape
3. require both row-level and pack-level structure audit improvement before the
   next human review
