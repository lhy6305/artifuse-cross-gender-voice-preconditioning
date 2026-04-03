# Encodec Filter Side Envelope Probe Rejected v1

## Summary

This checkpoint records the first `Encodec` anchored `filter-side` injection
prototype after the `mel residual` surface was closed.

The tested shape was:

- source `Encodec 24khz` roundtrip anchor
- masked ATRR target delta converted into a low-quefrency envelope target
- source-phase-preserving spectral-envelope reconstruction

Result:

- runnable
- still structurally cleaner than the rejected BigVGAN family
- but worse than the plain `Encodec` roundtrip baseline on both targetward
  shift and structure risk

So the first `filter-side envelope` surface is rejected as the next active
prototype family.

The `Encodec` anchor family remains open.

## New Prototype Asset

A new script now exists:

- `scripts/run_encodec_atrr_filter_probe.py`

This script:

1. roundtrips each source row through `Encodec 24khz`
2. loads the exported ATRR target package
3. applies the same voiced and core-masked target delta logic used in the
   earlier `mel residual` probes
4. converts that masked delta into a low-order spectral-envelope target
5. reconstructs output with source phase preserved
6. writes a queue-shaped output for the existing machine diagnostics

## Tested Variants

Two fixed8 machine-only variants were tested:

1. strict low-order envelope
   - keep coeffs `12`
   - delta scale `0.20`
   - delta cap `1.50 dB`
   - gain floor `-1.50 dB`
   - gain cap `1.50 dB`
   - off-core scale `0.00`
2. wider low-order envelope with slight leakage
   - keep coeffs `16`
   - delta scale `0.35`
   - delta cap `2.00 dB`
   - gain floor `-2.00 dB`
   - gain cap `2.00 dB`
   - off-core scale `0.15`

Outputs:

- `artifacts/diagnostics/encodec_atrr_filter_probe/v1_fixed8_env12_s020_d15_g15_bw24/`
- `artifacts/diagnostics/encodec_atrr_filter_probe/v2_fixed8_env16_s035_d20_g20_off015_bw24/`

## Comparison Against The Encodec Roundtrip Anchor

Plain `Encodec` roundtrip baseline:

- targetward shift score: `42.08`
- structure risk: `18.39`

Earlier best `core-masked mel residual` reference:

- strict: `42.33` shift, `20.93` structure risk
- off-core `0.15`: `42.42` shift, `22.13` structure risk

New `filter-side envelope` probe:

- strict low-order envelope: `39.42` shift, `20.66` structure risk
- wider low-order envelope with leakage: `37.95` shift, `22.16` structure risk

Reading:

- both filter-side variants regress targetward movement below the plain
  `Encodec` roundtrip baseline
- the stricter variant stays somewhat cleaner than the old `mel residual`
  variants, but that does not matter because the targetward regression is large
- the wider variant regresses on both targetward movement and structure versus
  the stricter variant

So the `filter-side envelope` surface is not a stronger ATRR carrier than the
already rejected `mel residual` family.

## Supporting Diagnostics

Targetward diagnostics:

- `artifacts/diagnostics/encodec_atrr_filter_probe/v1_fixed8_env12_s020_d15_g15_bw24_distribution/RESONANCE_DISTRIBUTION_DIAGNOSTIC_SUMMARY.md`
- `artifacts/diagnostics/encodec_atrr_filter_probe/v2_fixed8_env16_s035_d20_g20_off015_bw24_distribution/RESONANCE_DISTRIBUTION_DIAGNOSTIC_SUMMARY.md`

Structure audit:

- `artifacts/diagnostics/speech_structure_audit/v6_encodec_filter_vs_roundtrip/SPEECH_STRUCTURE_AUDIT.md`

## Route Decision

- Keep the `Encodec` roundtrip-anchor family open.
- Reject the first `filter-side envelope` injection surface as the next active
  prototype.
- Do not send any current `Encodec` filter-side variant to human review.

## Why The Surface Is Rejected

The surface is not failing because of catastrophic artifact.

It is failing because:

- it still raises structure risk above the roundtrip ceiling
- but it also gives back targetward movement instead of improving it

That means the surface is too weak in the wrong way:

- narrower than the old `mel residual`
- but not directionally useful enough to justify more scalar retuning

## Immediate Next Step

The next prototype should keep the `Encodec` anchor but leave both currently
tested non-latent surfaces closed:

1. broad or masked `mel residual`
2. low-order `filter-side envelope`

So the next active candidate should now move to a true latent-side or code-side
injection boundary.
