# Task And Branch Map

## Active Workstreams

| Workstream | Status | Notes | Key Files |
| --- | --- | --- | --- |
| Documentation language and encoding normalization | Completed | Active living docs were normalized to English ASCII and UTF-8 no-BOM safe maintenance rules. | `docs/00_context_bootstrap.md`, `docs/02_pitfalls_log.md`, `docs/64_documentation_language_and_encoding_policy_v1.md` |
| Handoff-doc and experiment-record separation | Completed | `docs/01` and `docs/02` are now limited to global handoff state. Historical oversized content was split into archive docs, and future experiment records must use one numbered doc per record. | `docs/65_active_handoff_docs_and_experiment_record_policy_v1.md`, `docs/66_archive_repo_state_and_asset_inventory_from_old_01_v1.md`, `docs/67_archive_route_progress_log_from_old_01_v1.md`, `docs/68_archive_historical_pitfalls_from_old_02_v1.md` |
| Representation-layer main line | Active | `LSF` remains the active family. `v7` is now reviewed and confirms a narrower failure mode: the pack is audible but still uniformly too weak, and the user reports that the core resonance still does not appear to move. The route therefore moved from partial-band geometry tuning to resonance-distribution quantization planning. Both first-pass and refined diagnostics have now been run on `v7`, and the refined result points to weak targetward movement and low core coverage rather than pure over-localization. The edit-object plan was narrowed into `ATRR`, the offline simulator was implemented, the first simulator run plus narrow sweep were executed, the focused conservative sweep narrowed a reconstruction-facing candidate band, and the first reconstruction bridge has now been specified around a stable `LSF` carrier with cepstral fallback only for machine diagnostics. The current next active step is to implement the machine-only reconstruction prototype. | `docs/62_representation_layer_lsf_probe_v6.md`, `docs/63_representation_layer_lsf_probe_v7.md`, `docs/69_post_lsf_v7_review_and_resonance_distribution_hypothesis_v1.md`, `docs/70_resonance_distribution_quantization_plan_v1.md`, `docs/71_lsf_v7_resonance_distribution_diagnostic_first_pass_v1.md`, `docs/72_lsf_v7_resonance_distribution_diagnostic_refined_v2.md`, `docs/73_targetward_resonance_distribution_edit_object_v1.md`, `docs/74_additive_targetward_resonance_residual_method_v1.md`, `docs/75_atrr_offline_simulator_and_scoring_loop_v1.md`, `docs/76_atrr_offline_simulator_first_run_and_narrow_sweep_v1.md`, `docs/77_atrr_focused_sweep_candidate_band_v1.md`, `docs/78_atrr_conservative_reconstruction_bridge_v1.md`, `scripts/extract_resonance_distribution_diagnostics.py`, `scripts/simulate_targetward_resonance_residual.py`, `scripts/build_stage0_speech_lsf_listening_pack.py`, `scripts/build_stage0_speech_cepstral_listening_pack.py`, `artifacts/diagnostics/lsf_v7_resonance_distribution_v1/`, `artifacts/diagnostics/lsf_v7_resonance_distribution_v2/`, `artifacts/diagnostics/atrr_offline_simulator_v1/`, `artifacts/diagnostics/atrr_offline_simulator_sweep/`, `artifacts/diagnostics/atrr_offline_simulator_focused_sweep/`, `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v7.json` |
| Machine-first review process | Active and stable | Human review is gated by machine metrics, with an added post-review strength-escalation rule for packs that return uniformly too weak. | `docs/57_machine_first_review_gate_v1.md`, `scripts/build_listening_machine_gate_report.py` |
| Older method families | Closed or historical | Older families remain as historical checkpoints unless explicitly reactivated. | historical docs under `docs/` |

## Current Operational Rule

- Keep `docs/01` and `docs/02` limited to handoff-only content.
- Put each future experiment record into its own numbered doc.
- The current next-step discussion should target resonance-distribution modeling, not another blind strength bump.
- The first implementation result already exists, so the next step should refine the diagnostic definition rather than restarting from a blank plan.
- The refined diagnostic result, the first concrete edit-method definition, the first simulator run, the focused sweep, and the reconstruction-bridge plan now all exist, so the next step should be machine-only reconstruction implementation rather than more abstract planning.

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and file ownership.
