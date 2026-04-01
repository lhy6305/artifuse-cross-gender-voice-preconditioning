# Encodec Core Masked Residual Probe Rejected v1

## Summary

This checkpoint records the next `Encodec` anchored ATRR injection variant after
the first broad mel-residual probe was rejected as low leverage.

The new idea was to keep the same `Encodec 24khz` roundtrip anchor, but apply
the residual only inside a narrow ATRR core-support mask derived from:

- source distribution support
- target distribution support
- target occupancy support
- edited-frame core occupancy

Two fixed8 machine-only variants were tested:

1. strict core mask
   - same conservative scalar settings as the first broad residual
   - off-core scale `0.00`
2. core mask with small leakage
   - same stronger scalar settings as the first moderate residual
   - off-core scale `0.15`

Result:

- both variants are slightly better tradeoffs than their broad-residual
  counterparts
- but neither variant beats the plain `Encodec` roundtrip baseline by a
  meaningful targetward margin
- the effective support is also extremely narrow, only about `5.0%` to `7.5%`
  of mel bins on average

So the `core-masked mel residual` is also rejected as the next active
prototype.

The `Encodec` anchor family remains open.

## Outputs

Artifacts:

- `artifacts/diagnostics/encodec_atrr_residual_probe/v2_fixed8_coremask_s020_d15_g20_bw24/`
- `artifacts/diagnostics/encodec_atrr_residual_probe/v2_fixed8_coremask_s030_d20_g30_off015_bw24/`

Targetward diagnostics:

- `artifacts/diagnostics/encodec_atrr_residual_probe/v2_fixed8_coremask_s020_d15_g20_bw24_distribution/`
- `artifacts/diagnostics/encodec_atrr_residual_probe/v2_fixed8_coremask_s030_d20_g30_off015_bw24_distribution/`

Structure audit:

- `artifacts/diagnostics/speech_structure_audit/v5_encodec_coremask_vs_roundtrip_vs_broad/`

## Compared Packs

Plain `Encodec` roundtrip baseline:

- targetward shift score: `42.08`
- structure risk: `18.39`

First broad residual probe:

- conservative: `42.38` shift, `21.47` structure risk
- moderate: `42.90` shift, `23.35` structure risk

New core-masked residual probe:

- strict: `42.33` shift, `20.93` structure risk
- off-core `0.15`: `42.42` shift, `22.13` structure risk

## Reading

The new mask does improve the tradeoff inside the same mel-residual family:

- strict core masking is slightly cleaner than the first conservative broad
  residual
- the small-leakage version is also cleaner than the first moderate broad
  residual

But the improvement is not large enough to change the route decision.

Relative to the plain `Encodec` roundtrip anchor:

- targetward movement is still nearly flat
- structure cost is still clearly higher

So this is not yet a strong ATRR edit carrier.

## Route Decision

- Keep the `Encodec` anchor family open.
- Reject the `mel residual` injection surface as the next active prototype.
- Do not send any current `Encodec` injected variant to human review.

## Immediate Next Step

The next prototype should no longer inject ATRR through a broad or masked
mel-domain residual.

The next candidate surface should be narrower than mel residual and should stay
closer to the source-preserving carrier boundary, for example:

1. filter-side injection
2. latent-side injection

