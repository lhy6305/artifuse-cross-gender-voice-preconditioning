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

The remaining active main line is the `LSF` representation route.

## Current LSF State

### `v6`

- `LSF v6` changed the masculine target from broad dark tilt to lower-formant geometry with preserved air.
- Machine metrics were strong enough to justify human review.
- Formal human review concluded that the route stayed viable, but the whole pack was uniformly too weak.

### `v7`

- `LSF v7` is the direct strength-escalated follow-up to `v6`.
- It promotes the machine-sweep winner `balanced_strong_v7d`.
- It raises both masculine and feminine strength so the next review round is not dominated by global weakness.
- Formal human review is now complete.
- The pack is clearly more audible than `v6`, but still `too_weak` on all `8 / 8` rows.
- The user also reported that the core resonance still does not appear to move.
- The newest checkpoint for this state is `docs/69_post_lsf_v7_review_and_resonance_distribution_hypothesis_v1.md`.
- The next planning document for this route is `docs/70_resonance_distribution_quantization_plan_v1.md`.
- The first diagnostic implementation for that plan now exists in `scripts/extract_resonance_distribution_diagnostics.py`.
- The first diagnostic result is recorded in `docs/71_lsf_v7_resonance_distribution_diagnostic_first_pass_v1.md`.
- The refined diagnostic result is recorded in `docs/72_lsf_v7_resonance_distribution_diagnostic_refined_v2.md`.
- The next design step is now captured in `docs/73_targetward_resonance_distribution_edit_object_v1.md`.
- The first concrete method definition is now captured in `docs/74_additive_targetward_resonance_residual_method_v1.md`.
- The first offline implementation bridge is now captured in `docs/75_atrr_offline_simulator_and_scoring_loop_v1.md`.
- The first actual simulator run and narrow follow-up sweep are now captured in `docs/76_atrr_offline_simulator_first_run_and_narrow_sweep_v1.md`.
- The focused conservative sweep and current candidate band are now captured in `docs/77_atrr_focused_sweep_candidate_band_v1.md`.
- The first conservative reconstruction bridge is now captured in `docs/78_atrr_conservative_reconstruction_bridge_v1.md`.
- The first machine-only reconstruction prototype results are now captured in `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md`.

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
- `docs/62_representation_layer_lsf_probe_v6.md`
- `docs/63_representation_layer_lsf_probe_v7.md`
- `docs/69_post_lsf_v7_review_and_resonance_distribution_hypothesis_v1.md`
- `docs/70_resonance_distribution_quantization_plan_v1.md`
- `docs/71_lsf_v7_resonance_distribution_diagnostic_first_pass_v1.md`
- `docs/72_lsf_v7_resonance_distribution_diagnostic_refined_v2.md`
- `docs/73_targetward_resonance_distribution_edit_object_v1.md`
- `docs/74_additive_targetward_resonance_residual_method_v1.md`
- `docs/75_atrr_offline_simulator_and_scoring_loop_v1.md`
- `docs/76_atrr_offline_simulator_first_run_and_narrow_sweep_v1.md`
- `docs/77_atrr_focused_sweep_candidate_band_v1.md`
- `docs/78_atrr_conservative_reconstruction_bridge_v1.md`
- `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md`
- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v7.json`
- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v7/`
- `artifacts/diagnostics/lsf_v7_resonance_distribution_v1/`
- `artifacts/diagnostics/lsf_v7_resonance_distribution_v2/`
- `scripts/simulate_targetward_resonance_residual.py`
- `artifacts/diagnostics/atrr_offline_simulator_v1/`
- `artifacts/diagnostics/atrr_offline_simulator_sweep/`
- `artifacts/diagnostics/atrr_offline_simulator_focused_sweep/`
- `scripts/reconstruct_atrr_lsf_prototype.py`
- `artifacts/diagnostics/atrr_lsf_reconstruction_prototype_v5/`
- `scripts/build_stage0_speech_lsf_listening_pack.py`
- `scripts/build_stage0_speech_cepstral_listening_pack.py`

## Historical Archive Links

- `docs/66_archive_repo_state_and_asset_inventory_from_old_01_v1.md`
- `docs/67_archive_route_progress_log_from_old_01_v1.md`
- `docs/68_archive_historical_pitfalls_from_old_02_v1.md`

## Next Allowed Action

The ATRR LSF reconstruction prototype is now machine-viable.

The per-row metrics show that 6 of 8 rows improve shift score over observed v7,
all 8 rows improve core coverage, and brilliance and presence are preserved.

The next implementation-facing work is:

- build a listening pack from `atrr_lsf_reconstruction_prototype_v5` reconstructed audio
- run the machine gate (`scripts/build_listening_machine_gate_report.py`) against that pack
- only send to human review if the machine gate passes on all required checks