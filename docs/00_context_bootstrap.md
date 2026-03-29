# Project Context Bootstrap

## Repo Identity

- Repo name: `artifuse-cross-gender-voice-preconditioning`
- Internal short name: `RGP-Pre`
- Scope: research design, experiment planning, scripts, summaries, and checkpoints for cross-gender voice preconditioning around the RVC pipeline

## Repo Boundary

- In scope:
  - design docs
  - experiment configs
  - scripts
  - structured summaries
  - daily reports
  - small milestone checkpoints
- Out of scope by default:
  - raw or derived audio
  - large downloaded archives
  - most model weights and indexes
  - local secrets
  - one-off local ops scripts
  - local dependency copies

## Active Living Docs

Only the following files are treated as active living docs right now:

1. `docs/00_context_bootstrap.md`
2. `docs/64_documentation_language_and_encoding_policy_v1.md`
3. `docs/65_active_handoff_docs_and_experiment_record_policy_v1.md`
4. `docs/01_project_overview_and_plan.md`
5. `docs/02_pitfalls_log.md`
6. `docs/05_task_branch_map.md`
7. `docs/57_machine_first_review_gate_v1.md`
8. `docs/62_representation_layer_lsf_probe_v6.md`
9. `docs/63_representation_layer_lsf_probe_v7.md`
10. `docs/69_post_lsf_v7_review_and_resonance_distribution_hypothesis_v1.md`
11. `docs/70_resonance_distribution_quantization_plan_v1.md`
12. `docs/71_lsf_v7_resonance_distribution_diagnostic_first_pass_v1.md`
13. `docs/72_lsf_v7_resonance_distribution_diagnostic_refined_v2.md`
14. `docs/73_targetward_resonance_distribution_edit_object_v1.md`
15. `docs/74_additive_targetward_resonance_residual_method_v1.md`
16. `docs/75_atrr_offline_simulator_and_scoring_loop_v1.md`
17. `docs/76_atrr_offline_simulator_first_run_and_narrow_sweep_v1.md`
18. `docs/77_atrr_focused_sweep_candidate_band_v1.md`
19. `docs/78_atrr_conservative_reconstruction_bridge_v1.md`
20. `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md`

Historical docs and archive docs may remain in their original language until they become active again. If a historical doc is reactivated, it must be migrated to English ASCII before further maintenance.

## Read Order

When context must be restored, read in this order:

1. `docs/00_context_bootstrap.md`
2. `docs/64_documentation_language_and_encoding_policy_v1.md`
3. `docs/65_active_handoff_docs_and_experiment_record_policy_v1.md`
4. `docs/01_project_overview_and_plan.md`
5. `docs/02_pitfalls_log.md`
6. `docs/05_task_branch_map.md`
7. `docs/57_machine_first_review_gate_v1.md`
8. `docs/69_post_lsf_v7_review_and_resonance_distribution_hypothesis_v1.md`
9. `docs/70_resonance_distribution_quantization_plan_v1.md`
10. `docs/71_lsf_v7_resonance_distribution_diagnostic_first_pass_v1.md`
11. `docs/72_lsf_v7_resonance_distribution_diagnostic_refined_v2.md`
12. `docs/73_targetward_resonance_distribution_edit_object_v1.md`
13. `docs/74_additive_targetward_resonance_residual_method_v1.md`
14. `docs/75_atrr_offline_simulator_and_scoring_loop_v1.md`
15. `docs/76_atrr_offline_simulator_first_run_and_narrow_sweep_v1.md`
16. `docs/77_atrr_focused_sweep_candidate_band_v1.md`
17. `docs/78_atrr_conservative_reconstruction_bridge_v1.md`
18. `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md`
19. `docs/63_representation_layer_lsf_probe_v7.md`
20. `docs/62_representation_layer_lsf_probe_v6.md`

## Hard Rules

### 1. Active docs use English ASCII only

- Every active living doc must use English only.
- Every active living doc must stay ASCII only.
- No Chinese text is allowed in active living docs.
- No smart quotes, long dashes, or other non-ASCII punctuation are allowed in active living docs.
- Archived historical docs are exempt until they are reactivated.

### 2. User-facing replies stay in Simplified Chinese

- This repo policy affects docs, not chat replies.
- Regardless of the language used in docs, assistant replies to the user must stay in Simplified Chinese.

### 3. UTF-8 read discipline

- The repo text files are UTF-8.
- In PowerShell, text reads must always specify `-Encoding utf8`.
- If text looks garbled, first suspect a read path that fell back to the local code page, usually GBK in this environment.

### 4. Avoid PowerShell text writes for repo docs

- Do not rely on PowerShell text write cmdlets for repo doc edits.
- In this environment, PowerShell UTF-8 writes may add a BOM, which is not wanted in this repo.
- Prefer repo-safe editors or edit paths that preserve UTF-8 without BOM.

### 5. Python entry point

- Use the repo root `.\python.exe` for project scripts.
- Do not mix in system `python` for project tasks unless there is a documented reason.

### 6. Git boundary

- Keep raw audio, large model assets, and local work dirs out of Git.
- Keep only lightweight configs, summaries, scripts, and small milestone checkpoints in Git.

### 7. PowerShell patch script discipline

- Do not use PowerShell heredocs or `-c` inline strings for Python patch scripts with nested quotes.
- Use `[System.IO.File]::WriteAllText` with a heredoc to write the patch file, then run it separately.
- This avoids quote mangling that causes SyntaxError in the patch script.

## Maintenance Rule

- If a new process rule, encoding issue, or environment trap is found, update `docs/02_pitfalls_log.md` and the relevant policy doc in the same task.
- If a new experiment or route checkpoint must be recorded, create a new numbered doc instead of expanding `docs/01_project_overview_and_plan.md` or `docs/02_pitfalls_log.md`.