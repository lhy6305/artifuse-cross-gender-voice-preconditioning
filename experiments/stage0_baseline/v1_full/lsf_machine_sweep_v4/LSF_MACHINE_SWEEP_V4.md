# LSF Machine Sweep V4

## Gate Thresholds

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

## Variant Ranking

### `mid_only_v4b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `78.49` / `71.29` / `76.28`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `1` / `1` / `1`
- description: Hold F3 at neutral and concentrate the masculine move into F2, testing whether the bottle effect is mostly a too-broad downward shift.

### `air_preserve_v4a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `78.10` / `70.35` / `75.51`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `1` / `2` / `1`
- description: Preserve the third resonance proxy for female-to-masculine edits so the result stops sounding like broad high-frequency suppression.

### `split_band_v4d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `76.77` / `68.30` / `73.47`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- description: Retune masculine search bands downward for F1/F2 only, while leaving the top band almost untouched to avoid the muffled bottle impression.

### `f2_focus_v4c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `76.65` / `67.95` / `73.53`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- description: Keep F1 and F3 near neutral while pushing F2 more assertively, aiming for tract-shape change without dulling upper-band air.

### `conservative_air_v4e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `72.97` / `61.37` / `66.83`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `2` / `2`
- description: Trade some masculine strength for safer high-band preservation, serving as a control against over-correction in the new selective-shift family.

