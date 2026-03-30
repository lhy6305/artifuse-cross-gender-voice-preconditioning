# Task And Branch Map

## Active Workstreams

| Workstream | Status | Notes | Key Files |
| --- | --- | --- | --- |
| Documentation language and encoding normalization | Completed | Active living docs normalized to English ASCII and UTF-8 no-BOM safe maintenance rules. | `docs/00_context_bootstrap.md`, `docs/02_pitfalls_log.md`, `docs/64_documentation_language_and_encoding_policy_v1.md` |
| Handoff-doc and experiment-record separation | Completed | `docs/01` and `docs/02` limited to global handoff state. Historical content split into archive docs. | `docs/65_active_handoff_docs_and_experiment_record_policy_v1.md` |
| ATRR distribution experiment | Closed | Offline simulator proved directional. LSF reconstruction bridge implemented and debugged (docs 74-79). Fundamental tension found: ATRR mel-distribution improvement and machine-gate spectral centroid effect cannot be satisfied simultaneously by the LSF carrier. Experiment closed. See doc 80. | `docs/74_additive_targetward_resonance_residual_method_v1.md` through `docs/80_atrr_reconstruction_dead_end_and_strength_escalation_pivot_v1.md`, `scripts/reconstruct_atrr_lsf_prototype.py` |
| LSF v8 review checkpoint | Completed | v8 machine results stayed strong, but human review showed that core resonance still does not move correctly. Female to male is still muffled and bottle like, with uneven effect across `f0`. Male to female overproduces upper band texture and plastic like noise. | `docs/81_lsf_v8_strength_escalation_machine_pass_v1.md`, `docs/82_post_lsf_v8_review_and_conditioned_priors_pivot_v1.md`, `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/`, `artifacts/machine_gate/lsf_v8/` |
| LSF conditioned priors pivot (v9) | Active - ready for human review | The conditioned `v9` family is implemented. `split_core_focus_v9a` and `f0_evening_v9b` passed the machine gate. `conservative_conditioned_v9c` did not. | `docs/82_post_lsf_v8_review_and_conditioned_priors_pivot_v1.md`, `docs/83_conditioned_lsf_v9_machine_sweep_v1.md`, `artifacts/diagnostics/lsf_v8_review_f0_summary/`, `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9/`, `scripts/run_lsf_machine_sweep.py`, `scripts/build_stage0_speech_lsf_listening_pack.py`, `scripts/summarize_lsf_review_by_f0.py` |
| Machine-first review process | Active and stable | Human review gated by machine metrics. Post-review strength escalation rule active. | `docs/57_machine_first_review_gate_v1.md`, `scripts/build_listening_machine_gate_report.py` |

## Current Operational Rule

- Keep `docs/01` and `docs/02` limited to handoff-only content.
- Put each future experiment record into its own numbered doc.
- The ATRR experiment is closed. Do not restart it without a new synthesis method.
- Do not do another direct strength escalation off `v8`.
- Conditioned `LSF v9` has already been built and machine-ranked.
- The immediate next step is human review on `split_core_focus_v9a`, with `f0_evening_v9b` as the optional comparison pack.

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and file ownership.
