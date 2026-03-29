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
- Machine gate: passes (avg quant 86.47, direction 81.05, effect 97.17).
- Machine gate recommendation: `escalate_strength_before_next_human`.
- ATRR distribution experiment (docs 70-79): correctly diagnosed low core coverage
  and weak targetward movement, but the ATRR LSF reconstruction bridge could not
  simultaneously achieve mel-distribution improvement and machine-gate-measurable
  spectral effect. Experiment closed. See doc 80 for full conclusion.

### `v8` (next)

- Direct strength escalation from v7.
- Raise center_shift_ratios and pair_width_ratios further.
- Run machine sweep to find strongest setting without preservation collapse.
- Build listening pack, run machine gate, submit for human review only if gate passes.
- Target: avg auto_quant_score >= 80, direction_score >= 70, preservation_score >= 95.

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
- `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md`
- `docs/80_atrr_reconstruction_dead_end_and_strength_escalation_pivot_v1.md`
- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v7.json`
- `scripts/build_stage0_speech_lsf_listening_pack.py`
- `scripts/run_lsf_machine_sweep.py`

## Historical Archive Links

- `docs/66_archive_repo_state_and_asset_inventory_from_old_01_v1.md`
- `docs/67_archive_route_progress_log_from_old_01_v1.md`
- `docs/68_archive_historical_pitfalls_from_old_02_v1.md`

## Next Allowed Action

Implement LSF v8 strength escalation:

1. Read `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v7.json`
   for current parameter values.
2. Define a v8 sweep grid that raises center_shift_ratios and pair_width_ratios
   beyond v7 levels.
3. Run the machine sweep (`scripts/run_lsf_machine_sweep.py` or equivalent).
4. Select the strongest config that keeps preservation_score >= 95 and no
   artifact flags.
5. Build listening pack and run machine gate.
6. Submit for human review only if machine gate passes.