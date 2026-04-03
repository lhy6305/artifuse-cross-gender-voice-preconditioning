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
15. `docs/85_lsf_route_closure_and_vocoder_pivot_prep_v1.md`
16. `docs/86_new_carrier_requirements_and_first_vocoder_bridge_prototype_v1.md`
17. `docs/87_vocoder_carrier_adapter_probe_v1.md`
18. `docs/88_local_rvc_posterior_bridge_probe_rejected_v1.md`
19. `docs/89_torchaudio_wavernn_domain_adapt_probe_rejected_v1.md`
20. `docs/90_local_bigvgan_probe_and_vocos_rejection_v1.md`
21. `docs/91_bigvgan_bounded_pitch_correction_probe_v1.md`
22. `docs/92_vctk_bigvgan_weak_row_diagnostics_v1.md`
23. `docs/93_p241_single_row_cap_sweep_nonmonotonicity_v1.md`
24. `docs/94_bigvgan_pre_vocoder_voiced_blend_full8_probe_v1.md`
25. `docs/95_first_atrr_vocoder_human_pack_ready_v1.md`
26. `docs/96_atrr_first_human_review_structural_distortion_reject_and_structure_audit_v1.md`
27. `docs/97_bigvgan_structure_first_anchor_sweep_v1.md`
28. `docs/98_selective_anchor_and_p230_pitch_rescue_fail_v1.md`
29. `docs/99_target_side_bin_gating_probe_v1.md`
30. `docs/100_strength_conditioned_bin_gate_rejected_v1.md`
31. `docs/101_f0_conditioned_bin_gate_probe_v1.md`
32. `docs/102_shape_conditioned_gate_probe_v1.md`
33. `docs/103_row_targeted_gate_baseline_and_second_human_pack_prep_v1.md`
34. `docs/104_second_atrr_row_targeted_human_pack_ready_v1.md`
35. `docs/105_row_targeted_bigvgan_second_human_reject_v1.md`
36. `docs/106_post_bigvgan_pivot_shortlist_and_encodec_roundtrip_probe_v1.md`
37. `docs/107_encodec_anchored_mel_residual_probe_rejected_v1.md`
38. `docs/108_encodec_core_masked_residual_probe_rejected_v1.md`
39. `docs/109_encodec_filter_side_envelope_probe_rejected_v1.md`
40. `docs/110_encodec_latent_side_low_rank_probe_v1.md`
41. `docs/111_encodec_code_side_soft_neighbor_probe_not_promoted_v1.md`
42. `docs/112_encodec_code_refit_probe_not_promoted_v1.md`
43. `docs/113_encodec_teacher_shortlist_code_probe_not_promoted_v1.md`
44. `docs/114_encodec_code_gate_probe_not_promoted_v1.md`
45. `docs/115_encodec_code_commit_probe_not_promoted_v1.md`
46. `docs/116_encodec_code_hybrid_probe_not_promoted_v1.md`
47. `docs/117_encodec_latent_structured_probe_not_promoted_v1.md`
48. `docs/118_encodec_latent_soft_support_probe_not_promoted_v1.md`
49. `docs/119_encodec_latent_distribution_objective_probe_not_promoted_v1.md`
50. `docs/120_encodec_latent_dual_objective_probe_not_promoted_v1.md`

## Read Order

When context must be restored, read in this order:

1. `docs/00_context_bootstrap.md`
2. `docs/01_project_overview_and_plan.md`
3. `docs/02_pitfalls_log.md`
4. `docs/05_task_branch_map.md`
5. `docs/82_post_lsf_v8_review_and_conditioned_priors_pivot_v1.md`
6. `docs/83_conditioned_lsf_v9_machine_sweep_v1.md`
7. `docs/84_v9_sample_drift_invalidation_and_fixed8_review_policy_v1.md`
8. `docs/85_lsf_route_closure_and_vocoder_pivot_prep_v1.md`
9. `docs/86_new_carrier_requirements_and_first_vocoder_bridge_prototype_v1.md`
10. `docs/87_vocoder_carrier_adapter_probe_v1.md`
11. `docs/88_local_rvc_posterior_bridge_probe_rejected_v1.md`
12. `docs/89_torchaudio_wavernn_domain_adapt_probe_rejected_v1.md`
13. `docs/90_local_bigvgan_probe_and_vocos_rejection_v1.md`
14. `docs/91_bigvgan_bounded_pitch_correction_probe_v1.md`
15. `docs/92_vctk_bigvgan_weak_row_diagnostics_v1.md`
16. `docs/93_p241_single_row_cap_sweep_nonmonotonicity_v1.md`
17. `docs/94_bigvgan_pre_vocoder_voiced_blend_full8_probe_v1.md`
18. `docs/95_first_atrr_vocoder_human_pack_ready_v1.md`
19. `docs/96_atrr_first_human_review_structural_distortion_reject_and_structure_audit_v1.md`
20. `docs/97_bigvgan_structure_first_anchor_sweep_v1.md`
21. `docs/98_selective_anchor_and_p230_pitch_rescue_fail_v1.md`
22. `docs/99_target_side_bin_gating_probe_v1.md`
23. `docs/100_strength_conditioned_bin_gate_rejected_v1.md`
24. `docs/101_f0_conditioned_bin_gate_probe_v1.md`
25. `docs/102_shape_conditioned_gate_probe_v1.md`
26. `docs/103_row_targeted_gate_baseline_and_second_human_pack_prep_v1.md`
27. `docs/104_second_atrr_row_targeted_human_pack_ready_v1.md`
28. `docs/105_row_targeted_bigvgan_second_human_reject_v1.md`
29. `docs/106_post_bigvgan_pivot_shortlist_and_encodec_roundtrip_probe_v1.md`
30. `docs/107_encodec_anchored_mel_residual_probe_rejected_v1.md`
31. `docs/108_encodec_core_masked_residual_probe_rejected_v1.md`
32. `docs/109_encodec_filter_side_envelope_probe_rejected_v1.md`
33. `docs/110_encodec_latent_side_low_rank_probe_v1.md`
34. `docs/111_encodec_code_side_soft_neighbor_probe_not_promoted_v1.md`
35. `docs/112_encodec_code_refit_probe_not_promoted_v1.md`
36. `docs/113_encodec_teacher_shortlist_code_probe_not_promoted_v1.md`
37. `docs/114_encodec_code_gate_probe_not_promoted_v1.md`
38. `docs/115_encodec_code_commit_probe_not_promoted_v1.md`
39. `docs/116_encodec_code_hybrid_probe_not_promoted_v1.md`
40. `docs/117_encodec_latent_structured_probe_not_promoted_v1.md`
41. `docs/118_encodec_latent_soft_support_probe_not_promoted_v1.md`
42. `docs/119_encodec_latent_distribution_objective_probe_not_promoted_v1.md`
43. `docs/120_encodec_latent_dual_objective_probe_not_promoted_v1.md`
44. `docs/81_lsf_v8_strength_escalation_machine_pass_v1.md`
45. `docs/80_atrr_reconstruction_dead_end_and_strength_escalation_pivot_v1.md`
46. `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md`
47. `docs/57_machine_first_review_gate_v1.md`

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
