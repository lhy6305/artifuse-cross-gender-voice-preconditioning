# LSF Machine Sweep V5

## Gate Thresholds

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

## Variant Ranking

### `presence_bypass_plus_v5b`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `63.41` / `49.52` / `52.06`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- description: Push F2 a bit harder than v5a while still bypassing the upper presence and brilliance region from the original signal.

### `presence_bypass_v5a`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `63.40` / `48.96` / `51.54`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- description: Use a gradual original-band bypass above 1.8kHz so female-to-masculine keeps air while F1/F2 still move downward.

### `vctk_bypass_focus_v5d`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `62.58` / `47.60` / `50.66`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- description: Keep Libri masculine moderate but use a stronger bypass on the weakest VCTK masculine cell, targeting the main failure case first.

### `f2_only_bypass_v5c`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `62.33` / `47.28` / `50.23`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- description: Keep F1/F3 near neutral and rely on F2 plus an upper-band bypass, testing the narrowest tract-shift version of male direction.

### `gentle_bypass_control_v5e`

- decision: `borderline_review_optional`
- reason: `has_high_top_score_but_pack_average_is_weaker`
- avg quant / direction / effect: `61.85` / `45.11` / `48.34`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- description: Use a lighter F1/F2 shift with a strong original-band bypass as a control for separating muffling risk from sheer strength loss.

