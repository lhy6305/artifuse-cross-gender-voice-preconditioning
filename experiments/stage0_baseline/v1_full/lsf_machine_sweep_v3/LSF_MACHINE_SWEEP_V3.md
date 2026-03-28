# LSF Machine Sweep V3

## Gate Thresholds

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

## Variant Ranking

### `order20_rescue_v3e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `82.81` / `74.67` / `78.63`
- top score: `100.00`
- strong/pass/borderline/fail: `6` / `0` / `2` / `0`
- description: Raise LPC order to 20 and add a moderate strength bump, testing whether the remaining weakness is partly under-resolution rather than blend alone.

### `vctk_rescue_plus_v3b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `81.91` / `73.09` / `77.44`
- top score: `100.00`
- strong/pass/borderline/fail: `6` / `0` / `1` / `1`
- description: Keep Libri near v2 and spend almost all extra strength budget on the two VCTK cells, especially the still-weak masculine side.

### `masc_push_control_v3c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `81.78` / `72.97` / `77.44`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `4` / `0`
- description: Leave feminine nearly untouched and push both masculine cells harder, testing whether the remaining weakness is almost entirely on the female-to-masculine side.

### `fem_artifact_guard_v3d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `80.71` / `70.67` / `75.69`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `2` / `1`
- description: Pull Libri feminine back slightly while strengthening every other cell, explicitly trading a bit of male-to-feminine intensity for safer transients.

### `asym_boost_v3a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `80.67` / `70.97` / `75.90`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `2` / `1`
- description: Boost the newly audible v2 profile, but keep Libri feminine slightly trimmed to reduce the transient artifact noted in review.

