# Post BigVGAN Pivot Shortlist And Encodec Roundtrip Probe v1

## Summary

This checkpoint records the first concrete post-BigVGAN pivot step after the
second row-targeted BigVGAN human rejection.

The goal of this step was not another edited synthesis attempt.
It was to answer a stricter shortlist question first:

- which next carrier family has the best chance to preserve source structure
  strongly enough before another ATRR edit-injection experiment is attempted

The resulting shortlist decision is:

- move next to a source-preserving carrier family
- use `Encodec` as the first narrow prototype anchor
- do not continue the current direct `target_log_mel -> vocoder` family

## Why The Pivot Needed A New Screening Rule

The current route already proved that better machine targetward movement is not
enough.

The row-targeted BigVGAN stack improved machine structure metrics materially,
but human review still came back as:

- transformed rows are audible
- most rows still do not move core resonance correctly
- synthesis artifacts still dominate perception

So the next shortlist criterion must be:

- source-preserving naturalness ceiling first
- ATRR edit injection second

## Shortlist Result

### Rejected As The Next Active Family

Do not continue as the next active family:

1. more local threshold tuning on BigVGAN
2. another direct `target_log_mel -> generic mel vocoder` path
3. previously rejected `RVC posterior bridge`, `WaveRNN`, or `Vocos`

Reason:

- the direct target-mel bridge family can produce audible change
- but it is still too ready to let synthesis artifacts dominate perception

### Selected As The Next Active Family

The next active family is:

- source-preserving carrier with narrow edit injection

The first concrete candidate inside that family is:

- `Encodec 24khz` roundtrip anchor

Why this candidate won the shortlist:

- it is available in the local environment now
- it provides an analysis-synthesis prior instead of a pure target-mel decoder
- it is naturally aligned with the new requirement to preserve source structure
  before injecting ATRR edits

## New Probe

A new script now exists:

- `scripts/run_encodec_roundtrip_probe.py`

This script:

1. reads the fixed8 queue
2. runs source audio through `Encodec 24khz`
3. writes reconstructed audio
4. emits a queue-shaped csv for direct structure audit

This probe does not inject ATRR targets yet.
It only measures the source-preservation ceiling of the candidate carrier
family.

Output:

- `artifacts/diagnostics/encodec_roundtrip_probe/v1_fixed8_bw24/`

## Roundtrip Result

The roundtrip probe was audited against:

1. the rejected row-targeted BigVGAN human pack
2. the old fixed8 `LSF v9a` pack as a weak-but-structurally-clean control

Audit output:

- `artifacts/diagnostics/speech_structure_audit/v3_encodec_roundtrip_vs_rowtargeted_vs_lsf/SPEECH_STRUCTURE_AUDIT.md`

Pack-level result:

`Encodec 24kbps` roundtrip:

- avg logmel DTW L1: `0.5361`
- avg voiced overlap IoU: `0.9149`
- avg `F0` overlap MAE: `11.4966` cents
- avg structure risk score: `18.39`

Rejected row-targeted BigVGAN pack:

- avg logmel DTW L1: `0.7188`
- avg voiced overlap IoU: `0.7450`
- avg `F0` overlap MAE: `77.9540` cents
- avg structure risk score: `31.01`

Old fixed8 `LSF v9a` control:

- avg logmel DTW L1: `0.3257`
- avg voiced overlap IoU: `0.9453`
- avg `F0` overlap MAE: `6.3389` cents
- avg structure risk score: `12.37`

Reading:

- `Encodec` is not as structurally clean as the old weak-`LSF` control
- but it is materially better than the rejected BigVGAN human candidate
- this is the first post-BigVGAN signal strong enough to justify a new active
  prototype family

## Active Prototype Plan

The next implementation should not jump directly to full latent editing.

The first narrow post-shortlist prototype should be:

- `Encodec` roundtrip anchor plus narrow ATRR edit injection on a smaller
  synthesis surface

Preferred first shape:

1. start from source `Encodec` roundtrip audio
2. inject only a narrow ATRR-guided spectral residual or filter surface
3. keep explicit source-closeness constraints
4. evaluate structure audit before any human review

This is intentionally different from the rejected BigVGAN path:

- source structure is preserved first
- the ATRR edit is introduced second
- the carrier is not asked to synthesize the whole target mel from scratch

## Route Decision

- Keep the ATRR target package family open.
- Close the current BigVGAN tuning family as an active human-review path.
- Promote the `Encodec` roundtrip-anchor family as the next active prototype
  direction.

## Immediate Next Step

Implement the first `Encodec` anchored ATRR edit-injection probe.

The prototype should stay narrow:

1. fixed8 only
2. machine-only
3. structure audit required
4. no human review unless source-structure remains near the roundtrip ceiling
