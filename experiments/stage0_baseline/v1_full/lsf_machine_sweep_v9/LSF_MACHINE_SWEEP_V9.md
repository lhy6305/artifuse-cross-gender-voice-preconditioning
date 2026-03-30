# LSF Machine Sweep V9

## Gate Thresholds

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

## Variant Ranking

### `split_core_focus_v9a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `66.24` / `50.46` / `66.37`
- top score: `83.64`
- strong/pass/borderline/fail: `4` / `1` / `2` / `5`
- description: Direction-split conditioned LSF: masculine narrows width growth to avoid bottle/muffle, feminine trims top-band push and preserves more original air.

### `f0_evening_v9b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `66.03` / `50.24` / `65.76`
- top score: `84.08`
- strong/pass/borderline/fail: `3` / `1` / `5` / `3`
- description: Spend more budget on the under-responsive buckets: high-f0 masculine gets extra F2/core push, low-f0 feminine keeps more motion before the air guard ramps up.

### `conservative_conditioned_v9c`

- decision: `skip_human_review`
- reason: `machine_gate_not_met`
- avg quant / direction / effect: `60.32` / `41.80` / `55.41`
- top score: `81.69`
- strong/pass/borderline/fail: `1` / `1` / `4` / `6`
- description: Lower-risk conditioned control: keep the direction split and F0 buckets, but reduce overall blend so the new family can be compared against a safer baseline.

