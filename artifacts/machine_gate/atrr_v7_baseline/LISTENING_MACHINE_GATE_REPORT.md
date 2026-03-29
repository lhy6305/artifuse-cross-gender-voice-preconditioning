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

### `stage0_speech_lsf_listening_pack/v7`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `86.47` / `81.05` / `97.17`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `2` / `1` / `0`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `8`
- strength escalation: `escalate_strength_before_next_human`

