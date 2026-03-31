# Task And Branch Map

## Active Workstreams

| Workstream | Status | Notes | Key Files |
| --- | --- | --- | --- |
| Documentation language and encoding normalization | Completed | Active living docs normalized to English ASCII and UTF-8 no-BOM safe maintenance rules. | `docs/00_context_bootstrap.md`, `docs/02_pitfalls_log.md`, `docs/64_documentation_language_and_encoding_policy_v1.md` |
| Handoff-doc and experiment-record separation | Completed | `docs/01` and `docs/02` limited to global handoff state. Historical content split into archive docs. | `docs/65_active_handoff_docs_and_experiment_record_policy_v1.md` |
| ATRR distribution experiment | Closed | Offline simulator proved directional. LSF reconstruction bridge implemented and debugged (docs 74-79). Fundamental tension found: ATRR mel-distribution improvement and machine-gate spectral centroid effect cannot be satisfied simultaneously by the LSF carrier. Experiment closed. See doc 80. | `docs/74_additive_targetward_resonance_residual_method_v1.md` through `docs/80_atrr_reconstruction_dead_end_and_strength_escalation_pivot_v1.md`, `scripts/reconstruct_atrr_lsf_prototype.py` |
| LSF v8 review checkpoint | Completed | v8 machine results stayed strong, but human review showed that core resonance still does not move correctly. Female to male is still muffled and bottle like, with uneven effect across `f0`. Male to female overproduces upper band texture and plastic like noise. | `docs/81_lsf_v8_strength_escalation_machine_pass_v1.md`, `docs/82_post_lsf_v8_review_and_conditioned_priors_pivot_v1.md`, `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/`, `artifacts/machine_gate/lsf_v8/` |
| LSF conditioned priors pivot (v9) | Closed | The restored fixed8 `v9a` human review came back effectively indistinguishable. `LSF` is closed as an active synthesis route and should not continue to `v10`. | `docs/82_post_lsf_v8_review_and_conditioned_priors_pivot_v1.md`, `docs/83_conditioned_lsf_v9_machine_sweep_v1.md`, `docs/84_v9_sample_drift_invalidation_and_fixed8_review_policy_v1.md`, `docs/85_lsf_route_closure_and_vocoder_pivot_prep_v1.md`, `experiments/stage0_baseline/v1_full/speech_lsf_fixed_review_manifest_v8.csv`, `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9_fixed8/`, `artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/`, `artifacts/listening_review_rollup/lsf_v9_fixed8_v9a/`, `artifacts/machine_gate/lsf_v9_fixed8_v9a/` |
| New synthesis-family pivot prep | Active - bounded BigVGAN mitigation is current best | The `ATRR` vocoder-bridge target export is complete and the carrier adapter boundary is now runnable. A bounded Griffin-Lim probe validated the boundary, the local `RVC` posterior bridge was rejected, `torchaudio WaveRNN` was rejected after backend-domain mel adaptation, and local `Vocos mel 24khz` was also rejected. The current best stack is local `BigVGAN 22khz 80band 256x` with backend-domain mel reconstruction, explicit RMS matching, and bounded post-vocoder pitch correction. Weak-row diagnostics now show two failure classes: package-limited rows and backend-instability rows, with `p241_005_mic1` as the clearest remaining backend-stability target. | `docs/80_atrr_reconstruction_dead_end_and_strength_escalation_pivot_v1.md`, `docs/85_lsf_route_closure_and_vocoder_pivot_prep_v1.md`, `docs/86_new_carrier_requirements_and_first_vocoder_bridge_prototype_v1.md`, `docs/87_vocoder_carrier_adapter_probe_v1.md`, `docs/88_local_rvc_posterior_bridge_probe_rejected_v1.md`, `docs/89_torchaudio_wavernn_domain_adapt_probe_rejected_v1.md`, `docs/90_local_bigvgan_probe_and_vocos_rejection_v1.md`, `docs/91_bigvgan_bounded_pitch_correction_probe_v1.md`, `docs/92_vctk_bigvgan_weak_row_diagnostics_v1.md`, `scripts/export_atrr_vocoder_bridge_targets.py`, `scripts/run_atrr_vocoder_carrier_adapter.py`, `artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/`, `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_gl_probe/`, `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_rvc_bridge/`, `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_wavernn_domainadapt_smoke2/`, `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_vocos_smoke2/`, `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_rmsmatch_full8/`, `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_rmsmatch_pitchcorr150_cap300_full8/` |
| Machine-first review process | Active and stable | Human review gated by machine metrics. Post-review strength escalation rule active. | `docs/57_machine_first_review_gate_v1.md`, `scripts/build_listening_machine_gate_report.py` |

## Current Operational Rule

- Keep `docs/01` and `docs/02` limited to handoff-only content.
- Put each future experiment record into its own numbered doc.
- The ATRR experiment is closed. Do not restart it without a new synthesis method.
- Do not do another direct strength escalation off `v8`.
- `LSF` is now closed as an active route.
- Do not continue to `LSF v10`.
- The immediate next step is to keep the bounded `BigVGAN` stack as the active backend and prioritize backend-stability diagnostics on `p241_005_mic1` before any human review.

## Branch Policy

- No special branch map is active right now.
- If real parallel branches appear later, record them here with task scope and file ownership.
