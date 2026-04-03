# Encodec Latent Dual Objective Probe Not Promoted v1

## Summary

- This checkpoint records the first `Encodec` latent-side follow-up that
  blends the active masked delta-fit latent baseline with the later direct
  distribution-objective family in one optimization.
- The new family keeps the masked voiced-only ATRR delta-fit as the primary
  objective, then adds:
  - gap-adaptive frame-level distribution matching
  - utterance-level target-distribution matching
  - source-energy anchoring
- Result: the family is runnable after one implementation fix, but the first
  fixed8 variant regresses the pack-level tradeoff and is not promoted.

## Implementation

- Script: `scripts/run_encodec_atrr_latent_dual_objective_probe.py`
- Core path:
  - start from the plain `Encodec 24khz` roundtrip anchor
  - keep the masked voiced-only ATRR delta-fit objective from the active
    latent baseline
  - add a gap-adaptive frame-level KL objective toward scaled edited frame
    distributions
  - add an utterance-level KL objective toward a scaled target-gender
    distribution
  - anchor frame energy and waveform drift back toward the source
- Important implementation correction:
  - the first smoke run exposed a frame-vs-bin weighting bug in the new
    objective
  - the fixed8 run uses the corrected script where frame-level distribution
    weights stay in frame space instead of being multiplied by the mel-bin
    core-support mask directly

## Full Fixed8 Run

### Dual-objective v1

- output:
  `artifacts/diagnostics/encodec_atrr_latent_dual_objective_probe/v1_fixed8_rank4_s020_d15_fk040_uk015_ea025_ds020_gf010_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_dual_objective_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_dual_objective_probe/v1_fixed8_rank4_s020_d15_fk040_uk015_ea025_ds020_gf010_bw24 `
  --voiced-only `
  --core-mask
```

## Results

### Distribution shift and structure comparison

| Pack | Avg targetward shift | Avg structure risk |
| --- | ---: | ---: |
| `Encodec roundtrip baseline` | `42.08` | `18.39` |
| `latent v1 conservative` | `42.29` | `17.56` |
| `latent distribution-objective v1` | `41.94` | `17.65` |
| `latent dual-objective v1` | `41.92` | `17.75` |

### Additional readings

- `dual-objective v1` distribution summary:
  - shift `41.92`
  - core coverage `57.89`
  - context consistency `56.45`
- `dual-objective v1` structure summary:
  - voiced overlap `0.9283`
  - `f0` overlap error `8.0541` cents
  - mean log-flatness delta `0.0240`
- optimization summary:
  - latent rms `0.0157`
  - delta loss `0.019111`
  - frame KL `3.119754`
  - utterance KL `0.514259`
  - frame-energy anchor `3.661644`

## Reading

- This family answers a useful route question directly:
  blending the active masked delta-fit baseline with extra distribution
  objectives does not recover the tradeoff that each family misses alone.
- Versus `latent v1`, the first tested variant gives back `0.37` of targetward
  shift and raises structure risk by `0.19`.
- Versus the earlier direct distribution-objective family, it gives back
  another `0.02` of shift and raises structure risk by `0.10`.
- Row-level reading is also not enough to justify promotion:
  - `1919_142785_000089_000003` is the only row that improves both axes versus
    `latent v1`, and the gain is only `+0.05` shift with `-0.15` structure
    risk
  - `p230_107_mic1` gains `+0.71` shift versus `latent v1`, but structure risk
    still rises by `+0.08`
  - `2086_149214_000006_000002` regresses materially versus `latent v1` at
    `-1.61` shift and `+0.75` structure risk
  - `p231_011_mic1` and `p226_011_mic1` also regress on both axes versus the
    active latent baseline
- So the blended objective is not failing because it is inactive.
- It is failing because the added distribution losses do not preserve the clean
  structure floor of `latent v1`, while the shift gains stay too small and too
  unevenly distributed across rows.

## Decision

- Keep `latent v1 conservative` as the active `Encodec` machine baseline.
- Keep `dual-objective v1` as a comparison checkpoint, not as a promoted
  baseline.
- Do not spend more route budget on nearby retuning of this current masked
  delta-fit plus gap-adaptive distribution blend family.
- If latent-side is revisited later, change the objective or support
  parameterization more fundamentally than the current:
  - masked delta-fit latent baseline
  - two-stage target-mover plus context-compensator split
  - soft support plus off-support null family
  - direct distribution-objective family
  - this masked delta-fit plus distribution blended family

## Artifacts

- `artifacts/diagnostics/encodec_atrr_latent_dual_objective_probe/smoke1/`
- `artifacts/diagnostics/encodec_atrr_latent_dual_objective_probe/v1_fixed8_rank4_s020_d15_fk040_uk015_ea025_ds020_gf010_bw24/`
- `artifacts/diagnostics/encodec_atrr_latent_dual_objective_probe/v1_fixed8_rank4_s020_d15_fk040_uk015_ea025_ds020_gf010_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v20_encodec_latent_dual_vs_latent_vs_distribution_vs_roundtrip/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
