# Encodec Latent Structured Probe Not Promoted v1

## Summary

- This checkpoint records the first two-stage `Encodec` latent-side follow-up
  after the native `code-side` comparison family also failed to replace
  `latent v1 conservative`.
- The new surface stays on the active `Encodec 24khz` roundtrip anchor, but it
  no longer uses a single latent delta only.
- Instead it splits the edit into:
  - a primary target mover on the masked ATRR support
  - a smaller context compensator that tries to keep off-core regions near
    zero while preserving the same target-side movement
- Result: the family is runnable and structurally clean, but it does not beat
  `latent v1 conservative` on the pack-level tradeoff and is not promoted.

## Implementation

- Script: `scripts/run_encodec_atrr_latent_structured_probe.py`
- Core path:
  - start from the plain `Encodec 24khz` roundtrip anchor
  - optimize a first low-rank latent delta against the masked ATRR target
    log-mel delta on the active support
  - optimize a second smaller low-rank latent delta on top of that target mover
  - regularize the second stage to keep off-core delta near zero while still
    fitting the same target support
  - keep waveform drift regularized back to the plain roundtrip anchor across
    both stages

## Full Fixed8 Run

### Structured latent v1

- output:
  `artifacts/diagnostics/encodec_atrr_latent_structured_probe/v1_fixed8_tr4_ts30_tc020_tl020_tt010_cr2_cs20_cc008_cl025_ct012_cn040_w100_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_structured_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_structured_probe/v1_fixed8_tr4_ts30_tc020_tl020_tt010_cr2_cs20_cc008_cl025_ct012_cn040_w100_bw24 `
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

### Additional readings

- `latent structured v1` distribution summary:
  - shift `42.13`
  - core coverage `58.23`
  - context consistency `55.92`
- `latent structured v1` structure summary:
  - voiced overlap `0.9336`
  - `f0` overlap error `7.8713` cents
  - mean log-flatness delta `0.0216`
- `latent structured v1` latent summary:
  - target delta rms `0.0080`
  - context delta rms `0.0020`
  - final core mel loss `0.004086`
  - final off-core energy `0.000128`

## Reading

- The second-stage context compensator is active, but it stays small relative
  to the primary target mover and does not produce a stronger pack-level
  tradeoff.
- Versus `latent v1`, the structured variant gives back `0.16` of targetward
  shift while structure risk is effectively tied at pack level.
- Row-level reading also does not justify promotion:
  - a few weak `VCTK` rows gain only tiny shift improvements
  - those gains are offset by small regressions on stronger `LibriTTS` rows
  - none of the known weak rows becomes a clear rescue case
- So the two-stage latent split answers a useful route question, but it does
  not replace the simpler one-stage latent baseline.

## Decision

- Keep `latent v1 conservative` as the active `Encodec` machine baseline.
- Keep `latent structured v1` as a comparison checkpoint, not as a promoted
  baseline.
- Do not spend more route budget on nearby target-mover plus context-compensator
  latent retuning.
- If latent-side is revisited later, change the objective or support
  parameterization more fundamentally than this two-stage split.

## Artifacts

- `artifacts/diagnostics/encodec_atrr_latent_structured_probe/smoke2/`
- `artifacts/diagnostics/encodec_atrr_latent_structured_probe/v1_fixed8_tr4_ts30_tc020_tl020_tt010_cr2_cs20_cc008_cl025_ct012_cn040_w100_bw24/`
- `artifacts/diagnostics/encodec_atrr_latent_structured_probe/v1_fixed8_tr4_ts30_tc020_tl020_tt010_cr2_cs20_cc008_cl025_ct012_cn040_w100_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v16_encodec_latent_structured_vs_latent_vs_roundtrip/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
