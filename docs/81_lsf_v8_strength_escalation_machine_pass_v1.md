# LSF v8 Strength Escalation Machine Pass v1

## Summary

This document records the direct strength-escalation pivot from v7 to v8 after
closing the ATRR reconstruction experiment.

The v8 goal was simple:

- follow the existing post-review rule
- raise strength because v7 human review came back 8/8 too_weak
- keep the machine gate green
- send the next pack to human review only after a fresh machine pass

## Why v8 Was Needed

v7 already passed the machine gate strongly:

- avg quant `86.47`
- avg direction `81.05`
- avg effect `97.17`

But human review still returned:

- `8 / 8 too_weak`

This is exactly the project rule for direct strength escalation.
The ATRR reconstruction experiment did not produce a better route, so the project
pivoted back to a stronger LSF package.

## Sweep

Implementation:

- `scripts/run_lsf_machine_sweep.py`
- new preset: `v8`

Sweep outputs:

- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v8/`
- `artifacts/listening_review/stage0_speech_lsf_machine_sweep_v8/`

Tested variants:

- `balanced_stronger_v8a`
- `masc_width_focus_v8b`
- `high_blend_v8c`
- `fem_focus_v8d`
- `conservative_v8e`

All 5 variants passed the machine gate.

## Winner Selection

The final v8 config is based on:

- `conservative_v8e`

Why this winner was selected:

- passes machine gate cleanly
- `5 strong_pass + 3 pass`
- `0 borderline + 0 fail`
- `0 risk rows`
- keeps the interpretation simple: one step above v7, not a large retune

The official config file is now:

- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v8.json`

## v8 Parameters

### Feminine

LibriTTS-R:

- `center_shift_ratios = [1.17, 1.12, 1.08]`
- `blend = 0.84`

VCTK Corpus 0.92:

- `center_shift_ratios = [1.18, 1.13, 1.09]`
- `blend = 0.86`

### Masculine

LibriTTS-R:

- `center_shift_ratios = [0.97, 0.84, 1.00]`
- `pair_width_ratios = [1.11, 1.26, 1.00]`
- `blend = 0.93`

VCTK Corpus 0.92:

- `center_shift_ratios = [0.96, 0.84, 1.00]`
- `pair_width_ratios = [1.09, 1.28, 1.00]`
- `blend = 0.93`
- `min_gap_hz = 60.0`

## Machine Result

Pack path:

- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/`

Machine queue outputs:

- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/listening_review_queue.csv`
- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/listening_review_quant_summary.md`

Gate outputs:

- `artifacts/machine_gate/lsf_v8/LISTENING_MACHINE_GATE_REPORT.md`

Pack summary:

- avg auto_quant_score: `87.77`
- avg auto_direction_score: `83.33`
- avg auto_preservation_score: `85.25`
- avg auto_effect_score: `98.81`
- strong/pass/borderline/fail: `5 / 3 / 0 / 0`
- machine gate decision: `allow_human_review`

## Interpretation

v8 is not an uncertain machine result.
It is cleanly machine-viable.

Compared with v7, the machine-side strength remains strong enough for review,
while the package removes the single borderline row and reaches a cleaner
`5 / 3 / 0 / 0` distribution.

This does not prove that v8 will solve the human `too_weak` verdict.
But it is the correct next package to send to human review.

## Immediate Next Step

Run formal human review on:

- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/`

If human review still returns a dominant `too_weak` verdict, the next step should
be another direct strength escalation or a new synthesis family, not a return to
ATRR reconstruction.