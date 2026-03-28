# LSF Machine Sweep V6

## Gate Thresholds

- `avg_auto_quant_score >= 65.00`
- `avg_auto_direction_score >= 45.00`
- `avg_auto_effect_score >= 45.00`
- and (`top_auto_quant_score >= 75.00` or `strongish_rows >= 2`)

## Variant Ranking

### `lower_geom_v6b`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `81.13` / `70.97` / `87.46`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `3` / `0`
- description: Concentrate more movement into F2 plus width expansion, testing a lower-formant geometry change without a broad dark tilt.

### `vctk_geom_focus_v6d`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `80.23` / `69.53` / `85.14`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `3` / `1`
- description: Keep Libri conservative but push VCTK masculine geometry harder, since the weakest failures have concentrated there so far.

### `lower_geom_v6a`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `79.31` / `67.81` / `84.63`
- top score: `100.00`
- strong/pass/borderline/fail: `5` / `0` / `1` / `2`
- description: Switch masculine rules to formant-lowering-with-air-preserve and widen the first two pairs slightly while keeping F3 neutral.

### `lower_geom_v6c`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `74.27` / `60.06` / `75.43`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `1` / `3`
- description: Use moderate center shifts but stronger pair-width growth, probing whether the audible male cue is more bandwidth-like than centroid-like.

### `conservative_geom_v6e`

- decision: `allow_human_review`
- reason: `meets_primary_machine_gate`
- avg quant / direction / effect: `70.51` / `54.86` / `65.68`
- top score: `100.00`
- strong/pass/borderline/fail: `4` / `0` / `0` / `4`
- description: A conservative control for the new formant-lowering family: smaller center moves, modest width changes, and more blend restraint.

