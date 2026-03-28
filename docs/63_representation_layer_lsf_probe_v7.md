# Representation Layer Route: LSF Probe v7

## Purpose

`LSF v7` is the strength-escalated follow-up to `v6`.

`v6` showed that the route direction was still viable but the whole pack was too weak. `v7` therefore keeps the same family and raises pack strength instead of changing method family again.

## Why `v7` Exists

The `v6` human result implied a narrow next step:

- keep the LSF route
- keep the lower-formant geometry idea
- raise strength before the next human pass

## Selection Logic

The `v7` machine-only sweep tested five stronger variants. All five passed the primary machine gate.

The promoted variant was:

- `balanced_strong_v7d`

It was selected because it raises both sides of the pack:

- stronger `female -> male`
- stronger `male -> female`

This avoids repeating a human review round that is dominated by global weakness.

## Machine Result

Pack-level machine metrics for the promoted `v7` pack:

- `avg_auto_quant_score = 86.47`
- `avg_auto_direction_score = 81.05`
- `avg_auto_effect_score = 97.17`
- `fail_rows = 0`

## Formal Pack

Formal config:

- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v7.json`

Formal pack:

- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v7/`

## Review-State Note

The user has already completed the latest human review for `v7`, but this task intentionally does not inspect that result.

This file therefore documents only the pre-review `v7` rationale and pack state, not the new human outcome.
