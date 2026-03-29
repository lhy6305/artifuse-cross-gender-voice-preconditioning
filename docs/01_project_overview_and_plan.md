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
- The current next step is formal human review of v8.

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
- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v8.json`
- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/`
- `artifacts/machine_gate/lsf_v8/`
- `scripts/run_lsf_machine_sweep.py`
- `scripts/build_stage0_speech_lsf_listening_pack.py`

## Next Allowed Action

The next action is formal human review of:

- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/`

Do not do more machine sweep work until the v8 human review result is in.