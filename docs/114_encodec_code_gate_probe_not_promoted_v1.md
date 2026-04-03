# Encodec Code Gate Probe Not Promoted v1

## Summary

- This checkpoint records the first sparse native `base <-> teacher code` gate
  family after the teacher-shortlist surface also failed to replace
  `latent v1`.
- The new surface is narrower than the earlier code families:
  - it does not mix over a neighbor shortlist
  - it does not hard-refit the whole editable code slice
  - it only learns a sparse gate between the base native code path and a fixed
    teacher-derived native code path
- Result: the family is runnable and very conservative, but it gives back too
  much targetward movement and is not promoted.

## Implementation

- Script: `scripts/run_encodec_atrr_code_gate_probe.py`
- Core path:
  - optimize the same masked low-rank latent teacher used by the active latent
    baseline family
  - derive a fixed native teacher-code path on the editable upper-quantizer
    slice through greedy native refit
  - learn a low-rank time-and-quantizer gate between the base native code path
    and that teacher native path
  - regularize gate magnitude, gate temporal roughness, and waveform drift back
    to the plain roundtrip anchor

## Full Fixed8 Run

### Sparse native code gate v1

- output:
  `artifacts/diagnostics/encodec_atrr_code_gate_probe/v1_fixed8_q24_n8_tr4_ts30_gr4_gs30_gb200_gt100_gl015_gtm007_gg020_w100_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_gate_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_code_gate_probe/v1_fixed8_q24_n8_tr4_ts30_gr4_gs30_gb200_gt100_gl015_gtm007_gg020_w100_bw24 `
  --voiced-only `
  --core-mask
```

## Results

### Distribution shift and structure comparison

| Pack | Avg targetward shift | Avg structure risk |
| --- | ---: | ---: |
| `Encodec roundtrip baseline` | `42.08` | `18.39` |
| `latent v1 conservative` | `42.29` | `17.56` |
| `code gate v1` | `42.02` | `17.57` |

### Additional readings

- `code gate v1` distribution summary:
  - shift `42.02`
  - core coverage `58.23`
  - context consistency `55.29`
- `code gate v1` structure summary:
  - voiced overlap `0.9338`
  - `f0` overlap error `7.8456` cents
  - mean log-flatness delta `0.0227`
- `code gate v1` gate summary:
  - gate mean `0.1011`
  - base keep mean `0.8989`
  - teacher-code gap rms `0.0417`

## Reading

- The sparse gate family is not failing on structural collapse.
- It is failing because the gate stays so conservative that targetward movement
  falls back to roughly the earlier conservative code-side level.
- The family therefore gives no useful tradeoff gain over `latent v1`:
  structure is essentially tied, but targetward shift is weaker.

## Decision

- Keep `latent v1 conservative` as the active `Encodec` machine baseline.
- Keep `code gate v1` as a comparison checkpoint, not as a promoted baseline.
- Do not spend more route budget on nearby retuning of this sparse native gate
  surface.
- If `code-side` is revisited later, change the parameterization more
  fundamentally than the current soft-neighbor, hard-refit, teacher-shortlist,
  and sparse-gate families.

## Artifacts

- `artifacts/diagnostics/encodec_atrr_code_gate_probe/smoke1/`
- `artifacts/diagnostics/encodec_atrr_code_gate_probe/v1_fixed8_q24_n8_tr4_ts30_gr4_gs30_gb200_gt100_gl015_gtm007_gg020_w100_bw24/`
- `artifacts/diagnostics/encodec_atrr_code_gate_probe/v1_fixed8_q24_n8_tr4_ts30_gr4_gs30_gb200_gt100_gl015_gtm007_gg020_w100_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v13_encodec_code_gate_vs_latent_vs_roundtrip/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
