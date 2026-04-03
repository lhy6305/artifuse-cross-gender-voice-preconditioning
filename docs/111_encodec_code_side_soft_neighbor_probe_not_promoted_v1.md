# Encodec Code-Side Soft Neighbor Probe Not Promoted v1

## Summary

- This checkpoint records the first true `Encodec` code-side comparison run
  after `latent v1` became the active machine baseline.
- The tested surface keeps the plain `Encodec 24khz` roundtrip anchor but
  replaces part of the quantized code stack through local soft mixing among
  nearby codebook neighbors.
- The goal was to test whether a narrower discrete boundary could beat the
  current latent baseline on both targetward movement and structure
  preservation.
- Result: both fixed8 code-side variants are runnable and structurally clean,
  but neither variant beats `latent v1 conservative` on both pack-level axes.
- So this first soft local code-side surface is not promoted as the new
  baseline.

## Implementation

- Script: `scripts/run_encodec_atrr_code_probe.py`
- Core path:
  - encode source with `Encodec`
  - keep the plain roundtrip code stack as the identity anchor
  - select an upper-quantizer slice as the editable code surface
  - gather local codebook neighbors for each active code position
  - optimize soft neighbor probabilities over time against the masked ATRR
    target log-mel delta
  - regularize code delta energy, time roughness, non-base code usage, and
    waveform `L1` distance back to the plain roundtrip anchor
- The probe stays local by construction:
  - only a quantizer subset is editable
  - each code position can move only among nearby codebook neighbors
  - an explicit identity bias keeps the base code path favored unless the
    target fit justifies leaving it

## Full Fixed8 Runs

### Conservative code baseline

- output:
  `artifacts/diagnostics/encodec_atrr_code_probe/v1_fixed8_q24_n8_k4_r4_s020_d15_cb020_ct010_nb005_w100_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_code_probe/v1_fixed8_q24_n8_k4_r4_s020_d15_cb020_ct010_nb005_w100_bw24 `
  --voiced-only `
  --core-mask
```

### Wider code comparison

- output:
  `artifacts/diagnostics/encodec_atrr_code_probe/v2_fixed8_q20_n12_k8_r8_s035_d20_cb010_ct005_nb002_w050_off015_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_code_probe/v2_fixed8_q20_n12_k8_r8_s035_d20_cb010_ct005_nb002_w050_off015_bw24 `
  --quantizer-start 20 `
  --quantizer-count 12 `
  --neighbor-count 8 `
  --rank 8 `
  --steps 40 `
  --init-scale 0.015 `
  --delta-scale 0.35 `
  --delta-cap-db 2.0 `
  --identity-bias 4.0 `
  --lambda-code-l2 0.10 `
  --lambda-code-time 0.05 `
  --lambda-nonbase 0.02 `
  --lambda-wave-l1 0.50 `
  --voiced-only `
  --core-mask `
  --core-mask-offcore-scale 0.15
```

## Results

### Distribution shift and structure comparison

| Pack | Avg targetward shift | Avg structure risk |
| --- | ---: | ---: |
| `Encodec roundtrip baseline` | `42.08` | `18.39` |
| `latent v1 conservative` | `42.29` | `17.56` |
| `latent v2 wider` | `42.40` | `18.09` |
| `code v1 conservative` | `42.01` | `17.57` |
| `code v2 wider` | `42.10` | `17.70` |

### Additional readings

- `code v1` distribution summary:
  - shift `42.01`
  - core coverage `58.27`
  - context consistency `55.38`
- `code v1` structure summary:
  - voiced overlap `0.9338`
  - `f0` overlap error `7.8737` cents
  - mean log-flatness delta `0.0227`
- `code v1` code summary:
  - non-base mass `0.0162`
  - base choice probability `0.9838`
- `code v2` distribution summary:
  - shift `42.10`
  - core coverage `58.00`
  - context consistency `55.80`
- `code v2` structure summary:
  - voiced overlap `0.9325`
  - `f0` overlap error `7.8766` cents
  - mean log-flatness delta `0.0301`
- `code v2` code summary:
  - non-base mass `0.1137`
  - base choice probability `0.8863`

## Reading

- The conservative code variant stays extremely close to the identity code
  path, which keeps structure almost tied with `latent v1`, but it does not
  move targetward enough to replace that latent baseline.
- The wider code variant increases non-base code usage by roughly seven times
  versus `code v1`, but the resulting targetward gain is still too small and
  structure gets slightly worse than `latent v1`.
- So the first soft local code-side family is not failing catastrophically.
  It is failing because it does not win the tradeoff against the already
  available latent baseline.

## Decision

- Keep `latent v1 conservative` as the active `Encodec` machine baseline.
- Keep `code v1` and `code v2` as comparison checkpoints, not as promoted
  baselines.
- Do not spend more route budget on nearby retuning of this same soft local
  code-neighbor surface.
- If the route revisits `code-side`, change the parameterization more
  fundamentally rather than widening the same local soft-neighbor design.

## Artifacts

- `artifacts/diagnostics/encodec_atrr_code_probe/smoke1/`
- `artifacts/diagnostics/encodec_atrr_code_probe/v1_fixed8_q24_n8_k4_r4_s020_d15_cb020_ct010_nb005_w100_bw24/`
- `artifacts/diagnostics/encodec_atrr_code_probe/v1_fixed8_q24_n8_k4_r4_s020_d15_cb020_ct010_nb005_w100_bw24_distribution/`
- `artifacts/diagnostics/encodec_atrr_code_probe/v2_fixed8_q20_n12_k8_r8_s035_d20_cb010_ct005_nb002_w050_off015_bw24/`
- `artifacts/diagnostics/encodec_atrr_code_probe/v2_fixed8_q20_n12_k8_r8_s035_d20_cb010_ct005_nb002_w050_off015_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v8_encodec_code_vs_latent_vs_roundtrip/`
- `artifacts/diagnostics/speech_structure_audit/v9_encodec_code_vs_latent_family/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
