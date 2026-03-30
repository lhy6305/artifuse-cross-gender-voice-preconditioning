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
- avg quant / direction / effect: `66.99` / `51.54` / `67.84`
- top score: `79.47`
- strong/pass/borderline/fail: `2` / `0` / `4` / `2`
- description: Direction-split conditioned LSF: masculine narrows width growth to avoid bottle/muffle, feminine trims top-band push and preserves more original air.

### `f0_evening_v9b`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `63.67` / `46.64` / `62.83`
- top score: `79.47`
- strong/pass/borderline/fail: `2` / `0` / `3` / `3`
- description: Spend more budget on the under-responsive buckets: high-f0 masculine gets extra F2/core push, low-f0 feminine keeps more motion before the air guard ramps up.

