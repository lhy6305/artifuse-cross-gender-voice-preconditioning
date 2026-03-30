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

### `stage0_speech_lsf_listening_pack/v8`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `87.77` / `83.33` / `98.81`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `3` / `0` / `0`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `3`
- strength escalation: `no_strength_escalation_flag`

