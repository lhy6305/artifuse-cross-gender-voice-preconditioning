# Encodec Latent Distribution Objective Probe Not Promoted v1

## Summary

- This checkpoint records the first `Encodec` latent-side follow-up that
  changes the optimization objective more fundamentally than the earlier
  delta-fit, two-stage latent split, and soft-support families.
- The new family does not fit `target_log_mel - source_log_mel` directly.
- Instead it optimizes the edited `Encodec` output against:
  - frame-level edited resonance distributions from the ATRR target package
  - utterance-level target resonance distribution
  - source frame-energy anchoring
- Result: the family is runnable and directionally interesting on a few rows,
  but the first fixed8 variant regresses the pack-level tradeoff and is not
  promoted.

## Implementation

- Script: `scripts/run_encodec_atrr_latent_distribution_probe.py`
- Core path:
  - start from the plain `Encodec 24khz` roundtrip anchor
  - optimize one low-rank latent delta before the decoder
  - decode waveform and mel each step
  - convert edited mel into normalized frame distributions
  - fit those distributions toward the ATRR edited frame distributions
  - also fit the voiced weighted utterance-average distribution toward the
    target-gender prototype distribution
  - anchor frame energy back toward the source and keep waveform drift
    regularized

## Full Fixed8 Run

### Distribution-objective v1

- output:
  `artifacts/diagnostics/encodec_atrr_latent_distribution_probe/v1_fixed8_rank4_ds035_fu100_uu050_ea050_w100_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_distribution_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_distribution_probe/v1_fixed8_rank4_ds035_fu100_uu050_ea050_w100_bw24 `
  --voiced-only
```

## Results

### Distribution shift and structure comparison

| Pack | Avg targetward shift | Avg structure risk |
| --- | ---: | ---: |
| `Encodec roundtrip baseline` | `42.08` | `18.39` |
| `latent v1 conservative` | `42.29` | `17.56` |
| `latent distribution-objective v1` | `41.94` | `17.65` |

### Additional readings

- `distribution-objective v1` distribution summary:
  - shift `41.94`
  - core coverage `57.57`
  - context consistency `57.10`
- `distribution-objective v1` structure summary:
  - voiced overlap `0.9333`
  - `f0` overlap error `8.2339` cents
  - mean log-flatness delta `0.0246`
- optimization summary:
  - latent rms `0.0311`
  - frame KL `2.975398`
  - utterance KL `0.484226`
  - frame-energy anchor `3.664276`

## Reading

- This family answers a useful route question directly:
  matching the edited frame distributions more explicitly does not
  automatically improve the actual pack-level targetward tradeoff.
- Versus `latent v1`, the first tested variant gives back `0.35` of targetward
  shift and also raises structure risk by `0.09`.
- Row-level reading is mixed rather than uniformly bad:
  - `p230_107_mic1` gains `+0.90` shift but structure risk rises by `+0.42`
  - `p231_011_mic1` gains a small `+0.12` shift while structure improves by
    `-0.41`
  - several stronger `LibriTTS` rows regress materially on shift, especially
    `2086_149214_000006_000002` at `-1.62`
- So the family is not failing because nothing happens.
- It is failing because the objective redistributes improvement across rows in a
  way that loses too much on stronger rows before the weak-row gains add up to
  a pack-level win.

## Decision

- Keep `latent v1 conservative` as the active `Encodec` machine baseline.
- Keep `distribution-objective v1` as a comparison checkpoint, not as a
  promoted baseline.
- Do not spend more route budget on nearby retuning of this current direct
  distribution-objective family.
- If latent-side is revisited later, change the objective more fundamentally
  than the current:
  - masked log-mel delta fitting
  - two-stage target-mover plus context-compensator split
  - soft support plus off-support null family
  - direct frame-distribution plus utterance-distribution objective

## Artifacts

- `artifacts/diagnostics/encodec_atrr_latent_distribution_probe/smoke1/`
- `artifacts/diagnostics/encodec_atrr_latent_distribution_probe/v1_fixed8_rank4_ds035_fu100_uu050_ea050_w100_bw24/`
- `artifacts/diagnostics/encodec_atrr_latent_distribution_probe/v1_fixed8_rank4_ds035_fu100_uu050_ea050_w100_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v19_encodec_latent_distribution_vs_latent_vs_roundtrip/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
