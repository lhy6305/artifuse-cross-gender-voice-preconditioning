# Encodec Code Hybrid Probe Not Promoted v1

## Summary

- This checkpoint records the first `Encodec` `code-side` hybrid family after
  the pure native `soft-neighbor`, `hard-refit`, `teacher-shortlist`,
  `sparse-gate`, and `hard-commit` surfaces all failed to replace
  `latent v1 conservative`.
- The new surface is not another nearby native-code retune:
  - first fit the same masked low-rank latent teacher used by the active
    latent baseline family
  - then greedily refit the editable upper-quantizer slice back into hard
    native `Encodec` codes
  - then allow only a small bounded continuous residual correction on top of
    that hard native scaffold
- Result: the family is runnable and interpretable, but the residual patch does
  not recover enough of the lost directionality and the pack is not promoted.

## Implementation

- Script: `scripts/run_encodec_atrr_code_hybrid_probe.py`
- Core path:
  - optimize the same masked low-rank latent teacher used by the active latent
    baseline family
  - project the editable upper-quantizer slice back into a hard native code
    scaffold
  - optimize a second bounded low-rank residual correction around that scaffold
  - regularize residual magnitude, residual temporal roughness, teacher-gap
    drift, and waveform drift back to the plain roundtrip anchor

## Full Fixed8 Run

### Code hybrid v1

- output:
  `artifacts/diagnostics/encodec_atrr_code_hybrid_probe/v1_fixed8_q24_n8_tr4_ts30_rr4_rs40_rc120_rl020_rt010_tg100_w100_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_hybrid_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_code_hybrid_probe/v1_fixed8_q24_n8_tr4_ts30_rr4_rs40_rc120_rl020_rt010_tg100_w100_bw24 `
  --residual-cap 0.12 `
  --residual-steps 40 `
  --lambda-teacher-gap 1.0 `
  --voiced-only `
  --core-mask
```

## Results

### Distribution shift and structure comparison

| Pack | Avg targetward shift | Avg structure risk |
| --- | ---: | ---: |
| `Encodec roundtrip baseline` | `42.08` | `18.39` |
| `latent v1 conservative` | `42.29` | `17.56` |
| `code refit v1` | `41.88` | `17.54` |
| `code hybrid v1` | `41.58` | `17.58` |

### Additional readings

- `code hybrid v1` distribution summary:
  - shift `41.58`
  - core coverage `57.14`
  - context consistency `55.17`
- `code hybrid v1` structure summary:
  - voiced overlap `0.9342`
  - `f0` overlap error `7.9665` cents
  - mean log-flatness delta `0.0220`
- `code hybrid v1` scaffold and residual summary:
  - scaffold teacher-gap rms `0.0351`
  - residual correction rms `0.0105`
  - final teacher-gap rms `0.0352`
  - changed code ratio `0.1531`

## Reading

- This hybrid family answers a useful route question: a small continuous repair
  around a hard native scaffold does not automatically recover the latent
  teacher advantage.
- On pack metrics it is actually weaker than the plain hard-refit checkpoint on
  both axes:
  - shift drops from `41.88` to `41.58`
  - structure risk rises from `17.54` to `17.58`
- So the bounded residual patch adds another optimization layer without buying
  back the directional loss that the hard native scaffold already introduced.
- The result behaves more like a mild local repair around the scaffold than a
  true restoration of the latent teacher path.

## Decision

- Keep `latent v1 conservative` as the active `Encodec` machine baseline.
- Keep `code hybrid v1` as a comparison checkpoint, not as a promoted
  baseline.
- Do not spend more route budget on nearby retuning of this hard-scaffold plus
  bounded-residual surface.
- If `code-side` is revisited later, change the parameterization more
  fundamentally than the current soft-neighbor, hard-refit,
  teacher-shortlist, sparse-gate, hard-commit, and code-hybrid families.

## Artifacts

- `artifacts/diagnostics/encodec_atrr_code_hybrid_probe/smoke1/`
- `artifacts/diagnostics/encodec_atrr_code_hybrid_probe/smoke2_rc120_tg100_rs40/`
- `artifacts/diagnostics/encodec_atrr_code_hybrid_probe/v1_fixed8_q24_n8_tr4_ts30_rr4_rs40_rc120_rl020_rt010_tg100_w100_bw24/`
- `artifacts/diagnostics/encodec_atrr_code_hybrid_probe/v1_fixed8_q24_n8_tr4_ts30_rr4_rs40_rc120_rl020_rt010_tg100_w100_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v15_encodec_code_hybrid_vs_latent_vs_roundtrip/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
