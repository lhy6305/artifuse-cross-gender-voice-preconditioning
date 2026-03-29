# Task And Branch Map

## Active Workstreams

| Workstream | Status | Notes | Key Files |
| --- | --- | --- | --- |
| Documentation language and encoding normalization | Completed | Active living docs were normalized to English ASCII and UTF-8 no-BOM safe maintenance rules. | `docs/00_context_bootstrap.md`, `docs/02_pitfalls_log.md`, `docs/64_documentation_language_and_encoding_policy_v1.md` |
| Handoff-doc and experiment-record separation | Completed | `docs/01` and `docs/02` are now limited to global handoff state. Historical oversized content was split into archive docs, and future experiment records must use one numbered doc per record. | `docs/65_active_handoff_docs_and_experiment_record_policy_v1.md`, `docs/66_archive_repo_state_and_asset_inventory_from_old_01_v1.md`, `docs/67_archive_route_progress_log_from_old_01_v1.md`, `docs/68_archive_historical_pitfalls_from_old_02_v1.md` |
| Representation-layer main line | Active | `LSF` remains the active family. `v7` is reviewed and confirms a narrower failure mode: audible but too weak, core resonance not moving. The route moved from partial-band geometry tuning to ATRR. The offline simulator was implemented and swept. The reconstruction bridge was specified and then implemented in `scripts/reconstruct_atrr_lsf_prototype.py`. Three bugs were found and fixed during implementation (local_strength normalization, per-frame ATRR target as fit objective, highband penalty weight). The v5 reconstruction run is machine-viable: 6/8 rows beat observed v7 on shift score, all 8 rows beat observed v7 on core coverage, brilliance and presence preserved. The next step is to build a listening pack from the v5 reconstructed audio and run the machine gate. | `docs/62_representation_layer_lsf_probe_v6.md`, `docs/63_representation_layer_lsf_probe_v7.md`, `docs/69_post_lsf_v7_review_and_resonance_distribution_hypothesis_v1.md`, `docs/70_resonance_distribution_quantization_plan_v1.md`, `docs/71_lsf_v7_resonance_distribution_diagnostic_first_pass_v1.md`, `docs/72_lsf_v7_resonance_distribution_diagnostic_refined_v2.md`, `docs/73_targetward_resonance_distribution_edit_object_v1.md`, `docs/74_additive_targetward_resonance_residual_method_v1.md`, `docs/75_atrr_offline_simulator_and_scoring_loop_v1.md`, `docs/76_atrr_offline_simulator_first_run_and_narrow_sweep_v1.md`, `docs/77_atrr_focused_sweep_candidate_band_v1.md`, `docs/78_atrr_conservative_reconstruction_bridge_v1.md`, `docs/79_atrr_lsf_reconstruction_prototype_v1_results.md`, `scripts/reconstruct_atrr_lsf_prototype.py`, `artifacts/diagnostics/atrr_lsf_reconstruction_prototype_v5/` |
| Machine-first review process | Active and stable | Human review is gated by machine metrics, with an added post-review strength-escalation rule for packs that return uniformly too weak. | `docs/57_machine_first_review_gate_v1.md`, `scripts/build_listening_machine_gate_report.py` |
| Older method families | Closed or historical | Older families remain as historical checkpoints unless explicitly reactivated. | historical docs under `docs/` |

## Current Operational Rule

- Keep `docs/01` and `docs/02` limited to handoff-only content.
- Put each future experiment record into its own numbered doc.
- The ATRR reconstruction prototype is now machine-viable. Do not do more abstract planning or simulator sweeps.
- The next concrete step is to build a listening pack from `atrr_lsf_reconstruction_prototype_v5` and run the machine gate.
- Do not send to human review until the machine gate passes.

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and file ownership.