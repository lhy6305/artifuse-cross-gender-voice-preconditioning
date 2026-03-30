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
8. `docs/63_representation_layer_lsf_probe_v7.md`
9. `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md`
10. `docs/80_atrr_reconstruction_dead_end_and_strength_escalation_pivot_v1.md`
11. `docs/81_lsf_v8_strength_escalation_machine_pass_v1.md`
12. `docs/82_post_lsf_v8_review_and_conditioned_priors_pivot_v1.md`
13. `docs/83_conditioned_lsf_v9_machine_sweep_v1.md`
14. `docs/84_v9_sample_drift_invalidation_and_fixed8_review_policy_v1.md`

## Read Order

When context must be restored, read in this order:

1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. `docs/05_task_branch_map.md`
5. `docs/82_post_lsf_v8_review_and_conditioned_priors_pivot_v1.md`
6. `docs/83_conditioned_lsf_v9_machine_sweep_v1.md`
7. `docs/84_v9_sample_drift_invalidation_and_fixed8_review_policy_v1.md`
8. `docs/81_lsf_v8_strength_escalation_machine_pass_v1.md`
9. `docs/80_atrr_reconstruction_dead_end_and_strength_escalation_pivot_v1.md`
10. `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md`
11. `docs/57_machine_first_review_gate_v1.md`

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
- Prefer `[System.IO.File]::WriteAllText` with explicit UTF8 encoding, or Python file writes.

### 5. Python entry point

- Use the repo root `.\python.exe` for project scripts.
- Do not mix in system `python` for project tasks unless there is a documented reason.

### 6. Git boundary

- Keep raw audio, large model assets, and local work dirs out of Git.
- Keep only lightweight configs, summaries, scripts, and small milestone checkpoints in Git.

### 7. PowerShell patch script discipline

- Do not use PowerShell `-c` inline strings for Python patch scripts with nested quotes.
- Use `[System.IO.File]::WriteAllText` to write the patch file, then run it separately.
- This avoids quote mangling that causes SyntaxError in the patch script.

## Maintenance Rule

- If a new process rule, encoding issue, or environment trap is found, update `docs/02_pitfalls_log.md` and the relevant policy doc in the same task.
- If a new experiment or route checkpoint must be recorded, create a new numbered doc instead of expanding `docs/01_project_overview_and_plan.md` or `docs/02_pitfalls_log.md`.
