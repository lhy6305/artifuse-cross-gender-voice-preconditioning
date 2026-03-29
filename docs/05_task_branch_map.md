# Task And Branch Map

## Active Workstreams

| Workstream | Status | Notes | Key Files |
| --- | --- | --- | --- |
| Documentation language and encoding normalization | Completed | Active living docs normalized to English ASCII and UTF-8 no-BOM safe maintenance rules. | `docs/00_context_bootstrap.md`, `docs/02_pitfalls_log.md`, `docs/64_documentation_language_and_encoding_policy_v1.md` |
| Handoff-doc and experiment-record separation | Completed | `docs/01` and `docs/02` limited to global handoff state. Historical content split into archive docs. | `docs/65_active_handoff_docs_and_experiment_record_policy_v1.md` |
| ATRR distribution experiment | Closed | Offline simulator proved directional. LSF reconstruction bridge implemented and debugged (docs 74-79). Fundamental tension found: ATRR mel-distribution improvement and machine-gate spectral centroid effect cannot be satisfied simultaneously by the LSF carrier. Experiment closed. See doc 80. | `docs/74_additive_targetward_resonance_residual_method_v1.md` through `docs/80_atrr_reconstruction_dead_end_and_strength_escalation_pivot_v1.md`, `scripts/reconstruct_atrr_lsf_prototype.py` |
| LSF strength escalation (v8) | Active - waiting human review | v7 human review was 8/8 too_weak, so v8 was built as the direct strength-escalated follow-up. The machine sweep is complete, `conservative_v8e` was selected, the official v8 pack was built, and the machine gate allows human review. | `docs/81_lsf_v8_strength_escalation_machine_pass_v1.md`, `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v8.json`, `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/`, `artifacts/machine_gate/lsf_v8/` |
| Machine-first review process | Active and stable | Human review gated by machine metrics. Post-review strength escalation rule active. | `docs/57_machine_first_review_gate_v1.md`, `scripts/build_listening_machine_gate_report.py` |

## Current Operational Rule

- Keep `docs/01` and `docs/02` limited to handoff-only content.
- Put each future experiment record into its own numbered doc.
- The ATRR experiment is closed. Do not restart it without a new synthesis method.
- The immediate next step is formal human review of `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/`.
- The v8 machine sweep is already complete and should not be rerun by default.
- Do not do more machine sweep work until the v8 human review result is in.

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and file ownership.
