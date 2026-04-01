# Encodec Anchored Mel Residual Probe Rejected v1

## Summary

This checkpoint records the first actual `Encodec` anchored ATRR edit-injection
prototype after the post-BigVGAN pivot shortlist.

The tested shape was:

- source `Encodec 24khz` roundtrip
- voiced-only bounded ATRR mel residual injection
- source-phase-preserving ISTFT reconstruction

Result:

- runnable
- structurally much cleaner than the rejected BigVGAN family
- but the injected edit adds only a tiny targetward gain over the plain
  `Encodec` roundtrip baseline

So this first injection shape is rejected as the next active prototype.

The `Encodec` anchor family itself remains open.

## New Prototype Asset

A new script now exists:

- `scripts/run_encodec_atrr_residual_probe.py`

This script:

1. roundtrips each source row through `Encodec 24khz`
2. loads the exported ATRR target package
3. applies a bounded voiced-only mel-domain residual
4. converts that residual into a narrow source-phase-preserving spectral gain
5. writes a queue-shaped output for existing machine diagnostics

## Tested Variants

Two fixed8 machine-only variants were tested:

1. conservative
   - delta scale `0.20`
   - delta cap `1.50 dB`
   - gain floor `-2.00 dB`
   - gain cap `2.00 dB`
2. moderate
   - delta scale `0.30`
   - delta cap `2.00 dB`
   - gain floor `-3.00 dB`
   - gain cap `3.00 dB`

Outputs:

- `artifacts/diagnostics/encodec_atrr_residual_probe/v1_fixed8_s020_d15_g20_bw24/`
- `artifacts/diagnostics/encodec_atrr_residual_probe/v1_fixed8_s030_d20_g30_bw24/`

## Comparison Against The Encodec Roundtrip Anchor

Roundtrip anchor only:

- targetward shift score: `42.08`
- structure risk: `18.39`

Conservative injected variant:

- targetward shift score: `42.38`
- structure risk: `21.47`

Moderate injected variant:

- targetward shift score: `42.90`
- structure risk: `23.35`

Reading:

- both injected variants are still much cleaner than the rejected BigVGAN
  human candidate
- but both add only a very small targetward gain over the plain roundtrip
  baseline
- that gain is too small for the amount of extra structure cost they introduce

## Supporting Diagnostics

Targetward diagnostics:

- `artifacts/diagnostics/encodec_roundtrip_probe/v1_fixed8_bw24_distribution/RESONANCE_DISTRIBUTION_DIAGNOSTIC_SUMMARY.md`
- `artifacts/diagnostics/encodec_atrr_residual_probe/v1_fixed8_s020_d15_g20_bw24_distribution/RESONANCE_DISTRIBUTION_DIAGNOSTIC_SUMMARY.md`
- `artifacts/diagnostics/encodec_atrr_residual_probe/v1_fixed8_s030_d20_g30_bw24_distribution/RESONANCE_DISTRIBUTION_DIAGNOSTIC_SUMMARY.md`

Structure audit:

- `artifacts/diagnostics/speech_structure_audit/v4_encodec_injected_vs_roundtrip_vs_bigvgan/SPEECH_STRUCTURE_AUDIT.md`

## Route Decision

- Keep the `Encodec` roundtrip-anchor family open.
- Reject this first mel-residual injection shape as the next active prototype.
- Do not send either tested injected variant to human review.

## Why The Shape Is Rejected

The core issue is not catastrophic failure.
It is low leverage.

The current shape behaves like:

- a relatively safe perturbation on top of the roundtrip anchor
- but not a strong enough ATRR edit carrier

So the route should not spend more time on nearby scalar retuning of this exact
shape.

## Immediate Next Step

Keep the `Encodec` anchor, but change the injection surface.

Most plausible next candidates:

1. a stricter core-masked residual that only acts on the ATRR core support
2. a narrower filter or latent-side injection instead of this broad mel-domain
   residual-to-gain projection
