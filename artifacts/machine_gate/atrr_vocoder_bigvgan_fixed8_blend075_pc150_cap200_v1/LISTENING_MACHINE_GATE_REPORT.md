# Listening Machine Gate Report v1

## Gate Policy

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

这个 gate 的目标不是证明方法成立，而是先过滤掉明显不值得上人工的包。

## Decision Counts

- allow_human_review: `0`
- borderline_review_optional: `0`
- skip_human_review: `1`

## Pack Summary

### `stage0_atrr_vocoder_bigvgan_fixed8/blend075_pc150_cap200_v1`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `48.33` / `40.84` / `40.84`
- top score: `66.24`
- strong/pass/borderline/fail: `0` / `2` / `5` / `1`
- reviewed outcome: `reviewed_non_null`
- reviewed too_weak rows: `0`
- strength escalation: `no_strength_escalation_flag`

