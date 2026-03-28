# LSF Machine Sweep v2

## Gate Thresholds

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

## Variant Ranking

### `order18_vctk_rescue_v2e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `78.85` / `68.09` / `73.71`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- description: Raise LPC order and retune VCTK search bands downward to rescue the weakest masculine cell without reopening WORLD/VTL.

### `masc_mid_focus_v2a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `77.05` / `65.31` / `70.65`
- top score: `100.00`
- strong/pass/borderline/fail: `3` / `0` / `3` / `2`
- description: Keep feminine side near v1, but strengthen masculine F2 shift first to avoid bottle-heavy F1 overpull.

### `order18_mid_focus_v2d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `76.95` / `65.16` / `70.74`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- description: Raise LPC order to 18 and focus the extra strength into the mid band, testing whether v1 was under-resolved.

### `masc_uniform_push_v2b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `76.67` / `64.79` / `70.77`
- top score: `100.00`
- strong/pass/borderline/fail: `3` / `0` / `3` / `2`
- description: Push masculine direction more uniformly across F1/F2/F3 while keeping feminine untouched for comparison.

### `balanced_pull_fem_push_masc_v2c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `72.88` / `59.35` / `64.71`
- top score: `100.00`
- strong/pass/borderline/fail: `3` / `0` / `3` / `2`
- description: Pull back feminine brightness slightly while pushing masculine direction harder to improve directional balance.

### `conservative_order18_control_v2f`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `70.07` / `55.27` / `60.80`
- top score: `92.42`
- strong/pass/borderline/fail: `3` / `0` / `2` / `3`
- description: Use order 18 but pull overall blend down to test whether v1 artifacts were mostly reconstruction pressure rather than wrong direction.

