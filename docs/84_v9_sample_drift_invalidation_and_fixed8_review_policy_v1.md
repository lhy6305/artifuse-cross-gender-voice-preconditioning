# v9 Sample Drift Invalidation And Fixed8 Review Policy v1

## Summary

The first human review attempt on conditioned `LSF v9` is not comparable to the
earlier `v8` review pack.

Reason:

- `v8` used the legacy fixed 8-sample pack
- the first `v9` sweep review packs used a new 12-sample selection with
  `f0_span` sampling
- only 1 utterance overlapped between `v8` and the first `v9a` review pack

This means the first `v9` human pass changed both:

- the processing family
- the listening sample set

That comparison is invalid as a continuation of the same listening track.

## What Happened

The conditioned `v9` sweep introduced:

- true `f0` conditioned rule dispatch
- `f0` span sampling
- 3 samples per cell instead of the old 2 samples per cell

This was useful for machine diagnosis, but it changed the listening pack
identity too much for cross-round human comparison.

The user correctly noticed that the new review pack audio was almost entirely
different from the older fixed pack.

That was not a listening mistake.
It was a pack construction drift.

## Current Human Conclusion For The Drifted v9 Pass

The user gave a pack-level conclusion and explicitly decided that no re-listen
is needed for the drifted `v9` pack.

Pack-level subjective result:

- most samples are not distinguishable before vs after
- a few female-to-male samples are locally distinguishable
- the distinguishable failure mode still behaves like broad pitch-like change
  without moving core resonance

Operational disposition:

- treat the first drifted `v9` human pass as functionally imperceptible
- do not use it as a strict row-by-row comparison continuation of `v8`

The partial queue contents from that pass are not the authoritative result.
The pack-level user conclusion is the authoritative record.

## New Fixed Review Rule

From this checkpoint forward:

- comparative human review on the active `LSF` line must reuse the same fixed
  legacy 8-sample review set until a deliberate review-set reset is declared
- any machine sweep may still use larger or `f0`-spread machine packs
- but the human comparison pack must stay stable across rounds

Canonical fixed review manifest:

- `experiments/stage0_baseline/v1_full/speech_lsf_fixed_review_manifest_v8.csv`

This manifest encodes the old `v8` review set and is now the required human
comparison baseline for follow-up `LSF` tests.

## Implementation

The build path now supports a fixed explicit selection manifest:

- `scripts/build_stage0_speech_lsf_listening_pack.py`
- `scripts/run_lsf_machine_sweep.py`

The fixed-manifest rerun outputs are here:

- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9_fixed8/`
- `artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/`

## Fixed8 Machine Result

On the restored legacy 8-sample pack:

1. `split_core_focus_v9a`
   - decision: `allow_human_review`
   - avg quant / direction / effect: `66.99 / 51.54 / 67.84`
2. `f0_evening_v9b`
   - decision: `borderline_review_optional`
   - avg quant / direction / effect: `63.67 / 46.64 / 62.83`

This means future listening can continue on a stable pack identity again.

## Next Action

Do not use the first drifted `v9` human pass as a valid cross-round comparison.

The next valid human comparison, if `LSF` work continues, must use:

1. the fixed 8-sample manifest
2. `split_core_focus_v9a` fixed8 as the first candidate
3. optional `f0_evening_v9b` fixed8 only as a comparison pack
