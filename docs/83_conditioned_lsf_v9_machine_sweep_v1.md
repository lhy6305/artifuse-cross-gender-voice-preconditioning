# Conditioned LSF v9 Machine Sweep v1

## Summary

The conditioned `LSF v9` pivot is now implemented and machine-validated.

This step changed the route from a plain strength escalation to a conditioned
family with:

- direction-specific priors
- `f0` bucketed rule matching
- `f0` span sample selection for machine sweep packs

The implementation now supports actual `f0` conditioned rule dispatch in the
`LSF` listening-pack builder, which was previously missing.

## Implementation Changes

The following script changes are now in place:

- `scripts/build_stage0_speech_lsf_listening_pack.py`
  - now matches rules with `domain + dataset_name + target_direction + f0`
  - now accepts `--selection-mode`
- `scripts/build_stage0_speech_listening_pack.py`
  - now supports `selection_mode = f0_span`
- `scripts/run_lsf_machine_sweep.py`
  - now supports `--samples-per-cell`
  - now supports `--selection-mode`
  - now supports preset `v9`
  - now expands rules into `low_f0 / mid_f0 / high_f0` buckets
- `scripts/summarize_lsf_review_by_f0.py`
  - added to summarize reviewed packs by direction and `f0` bucket

## v8 Diagnostic Outputs

The completed `v8` review is now summarized by `f0` bucket here:

- `artifacts/diagnostics/lsf_v8_review_f0_summary/`

Key signal:

- masculine side still trends weak in the reviewed low and mid buckets
- feminine side stays audible, but the reviewed mid and high buckets carry the
  artifact risk pattern

This agrees with the human report that the problem is now wrong distribution
and wrong landing zone, not only weak strength.

## v9 Sweep Setup

Base config:

- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v8.json`

Sweep outputs:

- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9/`
- `artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9/`

Sweep command used:

```powershell
.\python.exe .\scripts\run_lsf_machine_sweep.py `
  --preset v9 `
  --base-config experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v8.json `
  --input-csv experiments/fixed_eval/v1_2/fixed_eval_review_final_v1_2.csv `
  --sweep-dir experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9 `
  --pack-root artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9 `
  --samples-per-cell 3 `
  --selection-mode f0_span
```

## Machine Results

Pack summary:

- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9/lsf_machine_sweep_pack_summary.csv`

Ranking:

1. `split_core_focus_v9a`
   - decision: `allow_human_review`
   - avg quant / direction / effect: `66.24 / 50.46 / 66.37`
   - grades: `4 strong_pass + 1 pass + 2 borderline + 5 fail`
2. `f0_evening_v9b`
   - decision: `allow_human_review`
   - avg quant / direction / effect: `66.03 / 50.24 / 65.76`
   - grades: `3 strong_pass + 1 pass + 5 borderline + 3 fail`
3. `conservative_conditioned_v9c`
   - decision: `skip_human_review`
   - avg quant / direction / effect: `60.32 / 41.80 / 55.41`
   - grades: `1 strong_pass + 1 pass + 4 borderline + 6 fail`

## Interpretation

The conditioned family is viable.

This is the first point where the project has both:

- actual `f0` conditioned dispatch in code
- machine-pass candidates from the conditioned `LSF` route

However, the machine outputs still show that feminine `high_f0` remains the
weakest bucket family in the current conditioned variants.

`split_core_focus_v9a` is the best first human candidate because it is the
strongest aggregate machine result while explicitly prioritizing:

- anti bottle / anti muffle masculine edits
- anti plastic / anti over-bright feminine edits

`f0_evening_v9b` should be kept as the comparison candidate if one additional
human pack is allowed, because it spreads risk more evenly and reduces fail-row
count versus `v9a`.

## Next Action

The next action is no longer design only.

It is:

1. run human review on `split_core_focus_v9a`
2. optionally review `f0_evening_v9b` as the comparison pack
3. check whether masculine core resonance moves more clearly without the bottle
   color
4. check whether feminine high-band plastic texture is materially reduced

If both `v9a` and `v9b` still fail on the same subjective pattern, the next
step should be a synthesis family pivot rather than `LSF v10`.
