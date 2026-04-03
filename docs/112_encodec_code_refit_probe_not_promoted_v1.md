# Encodec Code Refit Probe Not Promoted v1

## Summary

- This checkpoint records the first harder `Encodec` `code-side` comparison
  after the soft local neighbor surface failed to beat `latent v1`.
- The new surface first optimizes a masked latent-side teacher on the plain
  `Encodec 24khz` roundtrip anchor, then projects that teacher back into a
  narrow native code boundary through hard greedy refit on the editable upper
  quantizer slice.
- The goal was to test whether a more native discrete boundary could keep the
  structural cleanliness of `latent v1` while retaining enough targetward
  movement to replace it.
- Result: the refit pack is structurally almost tied with `latent v1`, but it
  gives back too much targetward movement and is not promoted.

## Implementation

- Script: `scripts/run_encodec_atrr_code_refit_probe.py`
- Core path:
  - encode source with `Encodec`
  - keep the plain roundtrip code stack as the identity anchor
  - optimize a masked low-rank latent teacher on the same active support used
    by `latent v1`
  - isolate the editable upper-quantizer slice
  - greedily refit that slice back into native `Encodec` codes
  - decode the hard-refit code stack and score it with the existing
    distribution and structure audits

## Full Fixed8 Run

### Teacher-latent hard code refit

- output:
  `artifacts/diagnostics/encodec_atrr_code_refit_probe/v1_fixed8_q24_n8_teacherlatentv1_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_refit_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_code_refit_probe/v1_fixed8_q24_n8_teacherlatentv1_bw24 `
  --voiced-only `
  --core-mask
```

## Results

### Distribution shift and structure comparison

| Pack | Avg targetward shift | Avg structure risk |
| --- | ---: | ---: |
| `Encodec roundtrip baseline` | `42.08` | `18.39` |
| `latent v1 conservative` | `42.29` | `17.56` |
| `code v1 conservative` | `42.01` | `17.57` |
| `code refit v1` | `41.88` | `17.54` |

### Additional readings

- `code refit v1` distribution summary:
  - shift `41.88`
  - core coverage `57.35`
  - context consistency `55.28`
- `code refit v1` structure summary:
  - voiced overlap `0.9364`
  - `f0` overlap error `7.9480` cents
  - mean log-flatness delta `0.0230`
- `code refit v1` refit summary:
  - changed code ratio `0.1548`
  - teacher projection rms `0.0354`
  - teacher projection `L1` `0.0142`

## Reading

- The refit surface is not a failure of structural stability. It is a failure
  of tradeoff.
- Versus `latent v1`, the refit surface improves average structure risk by only
  `0.02`, which is effectively a tie at pack level.
- But it gives back `0.41` of targetward shift versus `latent v1`, and it also
  lands below the earlier conservative soft-neighbor code result on shift.
- The hard native code projection therefore appears to lose too much of the
  teacher benefit when forced back into the tested upper-quantizer slice.

## Decision

- Keep `latent v1 conservative` as the active `Encodec` machine baseline.
- Keep `code refit v1` as a comparison checkpoint, not as a promoted baseline.
- Do not spend more route budget on nearby retuning of this same hard-refit
  code surface.
- If `code-side` is revisited later, change the parameterization more
  fundamentally than either the current soft local neighbor surface or this
  teacher-latent hard refit.

## Artifacts

- `artifacts/diagnostics/encodec_atrr_code_refit_probe/smoke1/`
- `artifacts/diagnostics/encodec_atrr_code_refit_probe/v1_fixed8_q24_n8_teacherlatentv1_bw24/`
- `artifacts/diagnostics/encodec_atrr_code_refit_probe/v1_fixed8_q24_n8_teacherlatentv1_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v10_encodec_code_refit_vs_latent_vs_roundtrip/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
