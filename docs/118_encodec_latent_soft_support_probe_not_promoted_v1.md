# Encodec Latent Soft Support Probe Not Promoted v1

## Summary

- This checkpoint records the first `Encodec` latent-side follow-up that
  changes the support parameterization more fundamentally than the earlier
  binary-support `latent v1` and the later two-stage
  `target-mover plus context-compensator` split.
- The new family keeps a single latent delta, but it no longer fits the ATRR
  target on a flat binary core mask only.
- Instead it uses:
  - a soft time-frequency support map built from edited frame distributions,
    masked ATRR delta magnitude, and occupancy anchoring
  - an explicit off-support null penalty in the same one-stage objective
- Two fixed8 variants were tested.
- Result: the family is runnable and close, but neither tested variant beats
  `latent v1 conservative` on both pack-level axes.

## Implementation

- Script: `scripts/run_encodec_atrr_latent_support_probe.py`
- Core path:
  - start from the plain `Encodec 24khz` roundtrip anchor
  - build a soft time-frequency fit mask from the target package instead of a
    flat binary support only
  - optimize one low-rank latent delta against the masked ATRR target
  - add an off-support null penalty in the same objective so non-target regions
    stay near zero without a second optimization stage
  - keep waveform drift regularized back to the plain roundtrip anchor

## Full Fixed8 Runs

### Soft-support v1

- output:
  `artifacts/diagnostics/encodec_atrr_latent_support_probe/v1_fixed8_rank4_s020_d15_fb065_oa050_sf015_sp075_nf020_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_support_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_support_probe/v1_fixed8_rank4_s020_d15_fb065_oa050_sf015_sp075_nf020_bw24 `
  --voiced-only `
  --core-mask
```

### Soft-support v2 conservative

- output:
  `artifacts/diagnostics/encodec_atrr_latent_support_probe/v2_fixed8_rank4_s020_d15_fb080_oa040_sf010_sp090_nf015_ln030_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_support_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_support_probe/v2_fixed8_rank4_s020_d15_fb080_oa040_sf010_sp090_nf015_ln030_bw24 `
  --frame-blend 0.80 `
  --occupancy-anchor 0.40 `
  --support-floor 0.10 `
  --support-power 0.90 `
  --null-floor 0.15 `
  --lambda-null 0.30 `
  --voiced-only `
  --core-mask
```

## Results

### Distribution shift and structure comparison

| Pack | Avg targetward shift | Avg structure risk |
| --- | ---: | ---: |
| `Encodec roundtrip baseline` | `42.08` | `18.39` |
| `latent v1 conservative` | `42.29` | `17.56` |
| `latent structured v1` | `42.13` | `17.57` |
| `latent soft-support v1` | `42.32` | `17.57` |
| `latent soft-support v2 conservative` | `42.26` | `17.59` |

### Additional readings

- `latent soft-support v1` distribution summary:
  - shift `42.32`
  - core coverage `57.49`
  - context consistency `55.91`
- `latent soft-support v1` structure summary:
  - voiced overlap `0.9336`
  - `f0` overlap error `7.8796` cents
  - mean log-flatness delta `0.0220`
- `latent soft-support v2` distribution summary:
  - shift `42.26`
  - core coverage `57.65`
  - context consistency `55.73`
- `latent soft-support v2` structure summary:
  - voiced overlap `0.9329`
  - `f0` overlap error `7.8820` cents
  - mean log-flatness delta `0.0222`

## Reading

- `v1` is the closer result inside this new family.
- It improves average targetward shift over `latent v1` by only `0.03`, while
  giving back `0.01` of structure risk.
- That is not enough to clear the actual route gate.
- Row-level reading also stays too mixed to justify promotion:
  - `p231_011_mic1` gains `+0.23` shift, but structure risk also rises by
    `+0.07`
  - `1919_142785_000089_000003` gets a small structure gain at nearly tied
    shift
  - `174_50561_000024_000000` loses `0.18` shift while also getting slightly
    worse structurally
- `v2` answers the obvious follow-up question directly: a more conservative
  retune of the same support family does not rescue the tradeoff.
- It falls back to `42.26 / 17.59`, which is worse than both `latent v1` and
  `support v1`.

## Decision

- Keep `latent v1 conservative` as the active `Encodec` machine baseline.
- Keep `latent soft-support v1` and `v2` as comparison checkpoints, not as
  promoted baselines.
- Do not spend more route budget on nearby retuning of this current soft
  support family.
- If latent-side is revisited later, change the objective or support
  parameterization more fundamentally than the current:
  - binary-support one-stage latent baseline
  - two-stage target-mover plus context-compensator split
  - soft time-frequency support plus off-support null family

## Artifacts

- `artifacts/diagnostics/encodec_atrr_latent_support_probe/smoke1/`
- `artifacts/diagnostics/encodec_atrr_latent_support_probe/v1_fixed8_rank4_s020_d15_fb065_oa050_sf015_sp075_nf020_bw24/`
- `artifacts/diagnostics/encodec_atrr_latent_support_probe/v1_fixed8_rank4_s020_d15_fb065_oa050_sf015_sp075_nf020_bw24_distribution/`
- `artifacts/diagnostics/encodec_atrr_latent_support_probe/v2_fixed8_rank4_s020_d15_fb080_oa040_sf010_sp090_nf015_ln030_bw24/`
- `artifacts/diagnostics/encodec_atrr_latent_support_probe/v2_fixed8_rank4_s020_d15_fb080_oa040_sf010_sp090_nf015_ln030_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v17_encodec_latent_support_vs_latent_vs_roundtrip/`
- `artifacts/diagnostics/speech_structure_audit/v18_encodec_latent_support_family_vs_latent_vs_roundtrip/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
