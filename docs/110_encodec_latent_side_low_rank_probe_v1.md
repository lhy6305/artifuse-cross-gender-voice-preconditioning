# Encodec Latent-Side Low-Rank Probe v1

## Summary

- This checkpoint records the first true `Encodec` latent-side ATRR injection
  probe after the `mel residual` and `filter-side envelope` surfaces were
  closed.
- The new surface starts from the plain `Encodec 24khz` roundtrip anchor and
  injects a learned low-rank latent delta before the decoder.
- The latent delta is time-gated by voiced support and optimized against the
  masked ATRR target log-mel delta.
- The optimization is regularized by latent `L2`, latent temporal smoothness,
  and waveform `L1` distance back to the plain roundtrip anchor.
- This is the first injected `Encodec` family that beats the plain roundtrip
  baseline on both pack-level axes.

## Implementation

- Script: `scripts/run_encodec_atrr_latent_probe.py`
- Core path:
  - encode source with `Encodec`
  - decode quantized base latent for the plain roundtrip anchor
  - optimize a low-rank latent delta `A @ B`
  - gate the latent delta by voiced support in latent time
  - decode edited latent and fit the edited log-mel delta toward the masked
    ATRR target delta
- Loss terms:
  - weighted log-mel delta fit
  - latent `L2`
  - latent time-difference smoothness
  - waveform `L1` back to the plain roundtrip anchor

## Implementation Traps Found And Fixed

- `Encodec` decoder backward on `CUDA` failed through cuDNN RNN kernels while
  the model stayed in `eval` mode.
  - Fix: run the decoder forward path under
    `torch.backends.cudnn.flags(enabled=False)`.
- Exact-zero initialization for both low-rank factors created a bilinear dead
  start with zero gradient on both factors.
  - Fix: initialize both factors with small random noise through
    `--init-scale`.

## Full Fixed8 Runs

### Conservative latent baseline

- output:
  `artifacts/diagnostics/encodec_atrr_latent_probe/v1_fixed8_rank4_s020_d15_lc020_lt010_w100_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_probe/v1_fixed8_rank4_s020_d15_lc020_lt010_w100_bw24 `
  --voiced-only `
  --core-mask
```

### Wider latent comparison

- output:
  `artifacts/diagnostics/encodec_atrr_latent_probe/v2_fixed8_rank8_s035_d20_lc025_lt005_w050_off015_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_latent_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_latent_probe/v2_fixed8_rank8_s035_d20_lc025_lt005_w050_off015_bw24 `
  --delta-scale 0.35 `
  --delta-cap-db 2.0 `
  --rank 8 `
  --steps 40 `
  --init-scale 0.015 `
  --latent-cap 0.25 `
  --lambda-latent-l2 0.10 `
  --lambda-latent-time 0.05 `
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

### Additional readings

- `latent v1` distribution summary:
  - shift `42.29`
  - core coverage `58.46`
  - context consistency `55.76`
- `latent v1` structure summary:
  - voiced overlap `0.9340`
  - `f0` overlap error `7.8395` cents
  - mean log-flatness delta `0.0217`
- `latent v2` distribution summary:
  - shift `42.40`
  - core coverage `58.23`
  - context consistency `59.64`
- `latent v2` structure summary:
  - voiced overlap `0.9329`
  - `f0` overlap error `8.0506` cents
  - mean log-flatness delta `0.0510`

## Reading

- Both latent variants clear the plain roundtrip baseline on both pack-level
  axes.
- `latent v1` is the safer current machine baseline because it produces the
  larger structure improvement while keeping a small positive shift gain.
- `latent v2` is directionally stronger on targetward shift, but it also shows
  a visibly larger flatness increase and does not improve structure as much as
  `latent v1`.
- This is enough to keep the `Encodec` family active and to stop treating
  latent-side injection as a speculative fallback.

## Decision

- Promote `latent v1 conservative` as the current `Encodec` machine baseline.
- Keep `latent v2 wider` as a comparison point, not as the new baseline.
- Do not reopen `mel residual` or `filter-side envelope` tuning.
- The next comparison should be a true `code-side` boundary measured against
  `latent v1`, using the same fixed8 queue and the same distribution plus
  structure audits.

## Artifacts

- `artifacts/diagnostics/encodec_atrr_latent_probe/smoke2/`
- `artifacts/diagnostics/encodec_atrr_latent_probe/v1_fixed8_rank4_s020_d15_lc020_lt010_w100_bw24/`
- `artifacts/diagnostics/encodec_atrr_latent_probe/v1_fixed8_rank4_s020_d15_lc020_lt010_w100_bw24_distribution/`
- `artifacts/diagnostics/encodec_atrr_latent_probe/v2_fixed8_rank8_s035_d20_lc025_lt005_w050_off015_bw24/`
- `artifacts/diagnostics/encodec_atrr_latent_probe/v2_fixed8_rank8_s035_d20_lc025_lt005_w050_off015_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v7_encodec_latent_vs_roundtrip/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
