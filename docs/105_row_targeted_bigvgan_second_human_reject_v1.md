# Row Targeted BigVGAN Second Human Reject v1

## Summary

This checkpoint records the second fixed8 human review result for the ATRR
BigVGAN route.

The reviewed pack was:

- `artifacts/listening_review/stage0_atrr_vocoder_bigvgan_fixed8/rowveto_p230_override2086_025_v1/`

The result rejects the current row-targeted BigVGAN stack for further
human-review continuation.

This does not yet reject the ATRR target package family itself.

## Human Review Result

Formal rollup:

- `artifacts/listening_review_rollup/atrr_rowtargeted_v1/LISTENING_REVIEW_ROLLUP.md`

Pack-level outcome:

- reviewed: `8/8`
- audible: `yes=7`, `no=1`
- direction: `yes=0`, `maybe=1`, `no=6`, `n/a=1`
- artifact: `yes=7`, `no=1`
- proposed disposition: `reject`

Important caveat:

- the one `no/no` row is `p230_107_mic1`, which was intentionally carried as a
  source-anchor control row rather than an edited-row success

So the transformed-row reading is cleaner when that control row is excluded:

- transformed rows reviewed: `7`
- effect audible: `7/7`
- direction correct: `0/7 yes`, `1/7 maybe`, `6/7 no`
- artifact issue: `7/7 yes`

User-level reading from the completed review:

- there is some row-to-row separation now
- `7/8` do not move core resonance
- `1/8` changes voice color more clearly, but direction is still uncertain
- most rows still sound heavily synthesized

## Quantitative Context

To compare this pack against the earlier first human pass and the old fixed8
`LSF v9a` control, the structure audit was rerun on all three packs.

Outputs:

- `artifacts/diagnostics/speech_structure_audit/v2_rowtargeted_vs_firstpass_vs_lsf/SPEECH_STRUCTURE_AUDIT.md`

Main pack-level comparison:

Current row-targeted BigVGAN pack:

- avg logmel DTW L1: `0.7188`
- avg voiced overlap IoU: `0.7450`
- avg `F0` overlap MAE: `77.9540` cents
- avg structure risk score: `31.01`

Earlier first BigVGAN human pack:

- avg logmel DTW L1: `1.7401`
- avg voiced overlap IoU: `0.5996`
- avg `F0` overlap MAE: `255.1232` cents
- avg structure risk score: `58.03`

Old fixed8 `LSF v9a` control:

- avg logmel DTW L1: `0.3257`
- avg voiced overlap IoU: `0.9453`
- avg `F0` overlap MAE: `6.3389` cents
- avg structure risk score: `12.37`

Reading:

- the row-targeted stack is a real machine improvement over the first BigVGAN
  human pack
- but it is still much farther from source structure than the old weak-`LSF`
  control
- this matches the user's listening result: the route now produces more
  audible change, but still not clean core-resonance movement

## Route Decision

- Reject the current row-targeted BigVGAN stack for further human-review
  continuation.
- Do not schedule another BigVGAN human pass from this tuning family.
- Keep the ATRR target package family open.

## Why ATRR Is Not Closed Yet

This result is still not evidence that the ATRR target package is useless.

The stronger interpretation is:

- the route can now produce audible transformed outputs
- but the active BigVGAN carrier family still dominates perception with
  synthesis artifacts
- core-resonance judgment remains blocked on most rows

So the failure remains carrier-side and carrier-boundary-side, not necessarily
target-side.

## Immediate Next Step

Stop local threshold tuning on the current BigVGAN path.

The next active route step should be a carrier-family or carrier-boundary pivot
that aims for substantially higher naturalness before the next human review.

Most plausible next candidates:

1. a higher-fidelity inversion-capable carrier rather than the current
   mel-vocoder bridge
2. a new carrier path that preserves source structure more directly and only
   injects the ATRR edit in a narrower synthesis surface
