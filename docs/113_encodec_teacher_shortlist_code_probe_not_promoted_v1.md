# Encodec Teacher Shortlist Code Probe Not Promoted v1

## Summary

- This checkpoint records the first teacher-guided shortlist `Encodec`
  `code-side` family after both the soft local neighbor and hard native refit
  surfaces failed to replace `latent v1`.
- The new family keeps the latent-side teacher only as a target-aware native
  code shortlist builder.
- At each editable upper-quantizer position, the probe mixes softly among a
  small shortlist that includes the base code, the teacher-directed native code,
  and nearby native codes around that teacher-directed choice.
- This is materially different from the earlier code-side surfaces:
  - it does not stay local to the base-code neighborhood only
  - it does not collapse back to a hard greedy refit either
- Two fixed8 variants were tested.
- Both variants are runnable and closer to `latent v1` than the earlier code
  surfaces, but neither beats `latent v1` on both pack-level axes.

## Implementation

- Script: `scripts/run_encodec_atrr_code_teacher_probe.py`
- Core path:
  - optimize the same masked low-rank latent teacher used by the current latent
    baseline family
  - greedily derive a teacher-directed native code path on the editable
    quantizer slice
  - build a small native shortlist per position from base code plus
    teacher-directed candidates
  - optimize soft native-code mixing inside that shortlist against the ATRR
    target log-mel delta while regularizing teacher-projection gap, code energy,
    code roughness, non-base mass, and waveform drift

## Full Fixed8 Runs

### Teacher-shortlist v1

- output:
  `artifacts/diagnostics/encodec_atrr_code_teacher_probe/v1_fixed8_q24_n8_c6_tr4_ts30_sr4_ss30_tb030_ib250_tp050_cb010_ct005_nb002_w100_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_teacher_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_code_teacher_probe/v1_fixed8_q24_n8_c6_tr4_ts30_sr4_ss30_tb030_ib250_tp050_cb010_ct005_nb002_w100_bw24 `
  --voiced-only `
  --core-mask
```

### Teacher-shortlist v2 conservative

- output:
  `artifacts/diagnostics/encodec_atrr_code_teacher_probe/v2_fixed8_q24_n8_c6_tr4_ts30_sr4_ss30_ib350_tp050_cb015_ct007_nb003_w100_bw24/`
- command:

```powershell
.\python.exe .\scripts\run_encodec_atrr_code_teacher_probe.py `
  --output-dir artifacts/diagnostics/encodec_atrr_code_teacher_probe/v2_fixed8_q24_n8_c6_tr4_ts30_sr4_ss30_ib350_tp050_cb015_ct007_nb003_w100_bw24 `
  --identity-bias 3.5 `
  --lambda-code-l2 0.15 `
  --lambda-code-time 0.07 `
  --lambda-nonbase 0.03 `
  --voiced-only `
  --core-mask
```

## Results

### Distribution shift and structure comparison

| Pack | Avg targetward shift | Avg structure risk |
| --- | ---: | ---: |
| `Encodec roundtrip baseline` | `42.08` | `18.39` |
| `latent v1 conservative` | `42.29` | `17.56` |
| `code teacher v1` | `42.35` | `17.59` |
| `code teacher v2 conservative` | `42.26` | `17.58` |

### Additional readings

- `code teacher v1` distribution summary:
  - shift `42.35`
  - core coverage `58.12`
  - context consistency `55.71`
- `code teacher v1` structure summary:
  - voiced overlap `0.9330`
  - `f0` overlap error `7.8213` cents
  - mean log-flatness delta `0.0214`
- `code teacher v2` distribution summary:
  - shift `42.26`
  - core coverage `57.91`
  - context consistency `55.64`
- `code teacher v2` structure summary:
  - voiced overlap `0.9332`
  - `f0` overlap error `7.8196` cents
  - mean log-flatness delta `0.0222`

## Reading

- `v1` is the better directional result inside this new family because it is
  the only tested teacher-shortlist variant that clears `latent v1` on
  targetward shift.
- But `v1` still gives back `0.03` of structure versus `latent v1`, so it does
  not win the actual gate.
- `v2` tightened the teacher projection gap and reduced non-base mass
  materially, but that conservative retune only moved the pack to a near tie:
  it still lands slightly below `latent v1` on both targetward shift and
  structure.
- So this family is more promising than the earlier soft-neighbor and hard
  refit code surfaces, yet still not strong enough to replace the active latent
  baseline.

## Decision

- Keep `latent v1 conservative` as the active `Encodec` machine baseline.
- Keep `code teacher v1` and `code teacher v2` as comparison checkpoints, not
  as promoted baselines.
- Do not spend more route budget on nearby retuning of this current
  teacher-shortlist code surface.
- If `code-side` is revisited later, change the parameterization more
  fundamentally than the current soft-neighbor, hard-refit, and
  teacher-shortlist families.

## Artifacts

- `artifacts/diagnostics/encodec_atrr_code_teacher_probe/smoke1/`
- `artifacts/diagnostics/encodec_atrr_code_teacher_probe/v1_fixed8_q24_n8_c6_tr4_ts30_sr4_ss30_tb030_ib250_tp050_cb010_ct005_nb002_w100_bw24/`
- `artifacts/diagnostics/encodec_atrr_code_teacher_probe/v1_fixed8_q24_n8_c6_tr4_ts30_sr4_ss30_tb030_ib250_tp050_cb010_ct005_nb002_w100_bw24_distribution/`
- `artifacts/diagnostics/encodec_atrr_code_teacher_probe/v2_fixed8_q24_n8_c6_tr4_ts30_sr4_ss30_ib350_tp050_cb015_ct007_nb003_w100_bw24/`
- `artifacts/diagnostics/encodec_atrr_code_teacher_probe/v2_fixed8_q24_n8_c6_tr4_ts30_sr4_ss30_ib350_tp050_cb015_ct007_nb003_w100_bw24_distribution/`
- `artifacts/diagnostics/speech_structure_audit/v11_encodec_code_teacher_vs_latent_vs_roundtrip/`
- `artifacts/diagnostics/speech_structure_audit/v12_encodec_code_teacher_family_vs_latent_vs_roundtrip/`

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and
  file ownership.
