# LSF Machine Sweep V8

## Gate Thresholds

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

## Variant Ranking

### `fem_focus_v8d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `88.67` / `85.00` / `100.00`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `3` / `0` / `0`
- description: Spend most of the extra strength on feminine direction to test whether male-to-feminine weakness is the dominant remaining problem.

### `high_blend_v8c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `88.20` / `84.19` / `99.42`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `3` / `0` / `0`
- description: Push blend to 0.96 for masculine and 0.92 for feminine, with moderate center/width moves: tests whether blend ceiling is the bottleneck.

### `balanced_stronger_v8a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `88.14` / `84.50` / `99.64`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `3` / `0` / `0`
- description: Uniform strength escalation from v7d: push both directions one clear notch above the too_weak baseline.

### `masc_width_focus_v8b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `87.87` / `83.28` / `98.77`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `1` / `2` / `0`
- description: Push masculine pair-width harder than center shift, targeting resonance spread rather than pure centroid lowering.

### `conservative_v8e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `87.77` / `83.33` / `98.81`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `3` / `0` / `0`
- description: Conservative v8 control: modest step above v7d, serving as safety baseline if stronger variants collapse preservation.

