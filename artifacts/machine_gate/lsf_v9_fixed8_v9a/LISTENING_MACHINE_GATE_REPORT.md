# Listening Machine Gate Report v1

## Gate Policy

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

这个 gate 的目标不是证明方法成立，而是先过滤掉明显不值得上人工的包。

## Decision Counts

- allow_human_review: `1`
- borderline_review_optional: `0`
- skip_human_review: `0`

## Pack Summary

### `stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `66.99` / `51.54` / `67.84`
- top score: `79.47`
- strong/pass/borderline/fail: `2` / `0` / `4` / `2`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `4`
- strength escalation: `no_strength_escalation_flag`

