# Encodec Code Commit Probe Not Promoted v1

## Summary

- This checkpoint records the first fully discrete `Encodec` `code-side`
  commit-mask family after the sparse native gate surface also failed to
  replace `latent v1`.
- The new surface is more discrete than every earlier code-side family:
  - no neighbor softmix
  - no shortlist softmix
  - no continuous base-to-teacher interpolation at inference time
  - only a hard binary commit between base native code and teacher-derived
    native code
- Result: the family is runnable and structurally clean, but it gives back too
  much targetward movement and is not promoted.

## Implementation

- Script: `scripts/run_encodec_atrr_code_commit_probe.py`
- Core path:
  - optimize the same masked low-rank latent teacher used by the active latent
    baseline family
  - derive a fixed teacher-native code path on the editable upper-quantizer
    slice
  - learn a binary commit mask between the base native path and that
    teacher-native path through a straight-through training surrogate
  - regularize commit magnitude, commit temporal roughness, and waveform drift
    back to the plain roundtrip anchor

## Full Fixed8 Run

### Hard native code commit v1

- output:
  `artifacts/diagnostics/encodec_atrr_code_commit_probe/v1_fixed8_q24_n8_tr4_ts30_cr4_cs30_cb000_ct050_cl015_ctm007_cm010_w100_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_commit_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_code_commit_probe/v1_fixed8_q24_n8_tr4_ts30_cr4_cs30_cb000_ct050_cl015_ctm007_cm010_w100_bw24 `
  --commit-bias 0.0 `
  --commit-init-scale 0.05 `
  --commit-temperature 0.5 `
  --lambda-commit-mass 0.01 `
  --voiced-only `
  --core-mask
```

## Results

### Distribution shift and structure comparison

| Pack | Avg targetward shift | Avg structure risk |
| --- | ---: | ---: |
| `Encodec roundtrip baseline` | `42.08` | `18.39` |
| `latent v1 conservative` | `42.29` | `17.56` |
| `code commit v1` | `40.89` | `17.52` |

### Additional readings

- `code commit v1` distribution summary:
  - shift `40.89`
  - core coverage `58.03`
  - context consistency `54.48`
- `code commit v1` structure summary:
  - voiced overlap `0.9362`
  - `f0` overlap error `7.8787` cents
  - mean log-flatness delta `0.0227`
- `code commit v1` commit summary:
  - commit mean `0.1477`
  - base keep mean `0.8523`
  - teacher-code gap rms `0.0453`

## Reading

- The commit family is not a structural failure.
- It improves average structure risk versus `latent v1` by only `0.04`.
- But it gives back `1.40` of targetward shift versus `latent v1`, which is a
  much larger regression than the structural gain is worth.
- So the hard binary commit surface is too discrete in the wrong way: it is
  interpretable and clean, but directionally too weak.

## Decision

- Keep `latent v1 conservative` as the active `Encodec` machine baseline.
- Keep `code commit v1` as a comparison checkpoint, not as a promoted baseline.
- Do not spend more route budget on nearby retuning of this hard native commit
  surface.
- If `code-side` is revisited later, change the parameterization more
  fundamentally than the current soft-neighbor, hard-refit, teacher-shortlist,
  sparse-gate, and hard-commit families.

## Artifacts

- `artifacts/diagnostics/encodec_atrr_code_commit_probe/smoke1/`
- `artifacts/diagnostics/encodec_atrr_code_commit_probe/smoke2_bias0_init05_temp05/`
- `artifacts/diagnostics/encodec_atrr_code_commit_probe/v1_fixed8_q24_n8_tr4_ts30_cr4_cs30_cb000_ct050_cl015_ctm007_cm010_w100_bw24/`
- `artifacts/diagnostics/encodec_atrr_code_commit_probe/v1_fixed8_q24_n8_tr4_ts30_cr4_cs30_cb000_ct050_cl015_ctm007_cm010_w100_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v14_encodec_code_commit_vs_latent_vs_roundtrip/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
