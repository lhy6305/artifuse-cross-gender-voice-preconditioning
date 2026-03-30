# Project Overview And Plan

## Scope

This repo tracks research design, scripts, summaries, and controlled experiment state for cross-gender voice preconditioning around the RVC workflow.

This file is a handoff summary only. Detailed experiment history is stored in numbered checkpoint docs and archive docs.

## Current Operating Rules

- Active living docs must be English ASCII only.
- Repo text files are UTF-8 and should be read with explicit UTF-8 in PowerShell.
- Avoid PowerShell text write cmdlets for repo docs because of BOM risk in this environment.
- User-facing assistant replies must remain in Simplified Chinese.
- Use repo root `.\python.exe` for project scripts.
- For patch scripts with nested quotes, write via `[System.IO.File]::WriteAllText` then run separately.

## Route Summary

The project has already ruled out or deprioritized multiple route families, including:

- classic envelope-only variants
- conditional envelope transport
- low-rank envelope latent variants
- static neural envelope mapping
- conditioned envelope mapping
- probe-guided envelope-only residual variants
- source-filter residual v1 as a viable main line
- ATRR LSF reconstruction as a standalone upgrade path

The remaining active main line is the `LSF` representation route.

## Current LSF State

### `v7`

- `LSF v7` human review: 8/8 too_weak, core resonance does not appear to move.
- Machine gate: passes strongly.
- Machine gate recommendation: `escalate_strength_before_next_human`.

### `v8`

- `LSF v8` is the direct strength-escalated follow-up to v7.
- It is based on the `conservative_v8e` machine-sweep winner.
- Official config: `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v8.json`.
- The v8 pack has been built.
- Machine queue summary: `5 strong_pass + 3 pass + 0 borderline + 0 fail`.
- Machine gate: `allow_human_review`.
- Human review is now complete.
- Review summary: audible but still not moving core resonance correctly.
- Female to male still sounds muffled and bottle like, with uneven effect across `f0`.
- Male to female now shows excess upper band texture and plastic like noise.
- The post review machine report does not recommend another direct strength escalation.

### `v9`

- `LSF v9` is now implemented as a conditioned family, not a plain stronger `v8`.
- The code path now supports true `f0` conditioned rule dispatch and `f0` span
  sample selection.
- `v9` machine sweep outputs are in
  `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9/`.
- Machine-pass candidates:
  - `split_core_focus_v9a`
  - `f0_evening_v9b`
- Rejected control:
  - `conservative_conditioned_v9c`
- Current recommendation: send `split_core_focus_v9a` to human review first and
  keep `f0_evening_v9b` as the comparison pack if a second pass is allowed.
- The immediate technical goal remains to move core resonance more cleanly while
  reducing bottle like male artifacts and plastic like female artifacts.
- Important correction: the first `v9` human pass drifted away from the old
  `v8` listening set and is not a valid cross-round comparison.
- The user judged that drifted pass as functionally imperceptible and not worth
  re-listening.
- Comparative human review must now reuse the fixed manifest
  `experiments/stage0_baseline/v1_full/speech_lsf_fixed_review_manifest_v8.csv`.
- A fixed8 rerun is now available in
  `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9_fixed8/`.

## Process State

The project now uses a machine-first workflow:

1. build pack
2. build quantified review queue
3. run machine gate
4. send only machine-viable packs to human review

The workflow also includes a post-review strength rule:

- if a reviewed pack comes back mostly `too_weak`
- and artifacts are not the main problem
- then the next step is to raise strength before the next human pass

## Key Active Files

- `docs/00_context_bootstrap.md`
- `docs/64_documentation_language_and_encoding_policy_v1.md`
- `docs/65_active_handoff_docs_and_experiment_record_policy_v1.md`
- `docs/02_pitfalls_log.md`
- `docs/05_task_branch_map.md`
- `docs/57_machine_first_review_gate_v1.md`
- `docs/63_representation_layer_lsf_probe_v7.md`
- `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md`
- `docs/80_atrr_reconstruction_dead_end_and_strength_escalation_pivot_v1.md`
- `docs/81_lsf_v8_strength_escalation_machine_pass_v1.md`
- `docs/82_post_lsf_v8_review_and_conditioned_priors_pivot_v1.md`
- `docs/83_conditioned_lsf_v9_machine_sweep_v1.md`
- `docs/84_v9_sample_drift_invalidation_and_fixed8_review_policy_v1.md`
- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v8.json`
- `experiments/stage0_baseline/v1_full/speech_lsf_fixed_review_manifest_v8.csv`
- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/`
- `artifacts/diagnostics/lsf_v8_review_f0_summary/`
- `artifacts/machine_gate/lsf_v8/`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9/`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9_fixed8/`
- `artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9/`
- `artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/`
- `scripts/run_lsf_machine_sweep.py`
- `scripts/build_stage0_speech_lsf_listening_pack.py`
- `scripts/summarize_lsf_review_by_f0.py`

## Next Allowed Action

The next action is conditional:

1. do not rely on the first drifted `v9` human pass as a valid comparison
2. if human review continues, use the fixed8 pack only
3. review `split_core_focus_v9a` fixed8 first
4. use `f0_evening_v9b` fixed8 only as an optional comparison pack
5. if the fixed8 comparison still comes back effectively imperceptible or still
   misses core resonance, pivot synthesis family instead of escalating to
   `LSF v10`
