# LSF Machine Sweep V7

## Gate Thresholds

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

## Variant Ranking

### `balanced_strong_v7d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `86.47` / `81.05` / `97.17`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `2` / `1` / `0`
- description: Increase both feminine and masculine strength one notch so the next human package is not dominated by a global too-weak verdict.

### `vctk_strong_geom_v7c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `85.15` / `78.71` / `94.56`
- top score: `100.00`
- strong/pass/borderline/fail: `6` / `2` / `0` / `0`
- description: Spend most of the extra strength budget on VCTK masculine, while only modestly increasing Libri masculine to avoid needless artifact risk.

### `stronger_geom_v7a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `84.99` / `78.58` / `95.41`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `2` / `1` / `0`
- description: Raise blend and F2/width strength off the v6 winner so the new masculine family stops landing as uniformly too weak.

### `stronger_geom_v7b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `84.79` / `77.73` / `94.80`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `2` / `1` / `0`
- description: Keep F1 near v6 but push F2 and pair width harder, testing a more forceful male cue without reviving broad dark tilt.

### `conservative_plus_v7e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `84.70` / `77.59` / `94.17`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `1` / `2` / `0`
- description: A milder strength bump control, useful if the stronger v7 variants jump too fast into artifact-heavy territory.

