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

There is currently no active synthesis main line.

The `LSF` representation route has now been closed after the fixed8 `v9a`
human result.

The next active route-selection task is a new synthesis-family pivot.

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
- Human review is now complete.
- Review summary: audible but still not moving core resonance correctly.
- Female to male still sounds muffled and bottle like, with uneven effect across `f0`.
- Male to female now shows excess upper band texture and plastic like noise.
- The post review machine report does not recommend another direct strength escalation.

### `v9`

- `LSF v9` is now implemented as a conditioned family, not a plain stronger `v8`.
- The code path now supports true `f0` conditioned rule dispatch and `f0` span
  sample selection.
- `v9` machine sweep outputs are in
  `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9/`.
- Machine-pass candidates:
  - `split_core_focus_v9a`
  - `f0_evening_v9b`
- Rejected control:
  - `conservative_conditioned_v9c`
- Current recommendation: send `split_core_focus_v9a` to human review first and
  keep `f0_evening_v9b` as the comparison pack if a second pass is allowed.
- The immediate technical goal remains to move core resonance more cleanly while
  reducing bottle like male artifacts and plastic like female artifacts.
- Important correction: the first `v9` human pass drifted away from the old
  `v8` listening set and is not a valid cross-round comparison.
- The user judged that drifted pass as functionally imperceptible and not worth
  re-listening.
- Comparative human review must now reuse the fixed manifest
  `experiments/stage0_baseline/v1_full/speech_lsf_fixed_review_manifest_v8.csv`.
- A fixed8 rerun is now available in
  `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9_fixed8/`.
- Fixed8 human review is now complete for `split_core_focus_v9a`.
- Human result: effectively indistinguishable; no further relisten needed.
- Route decision: close `LSF` and do not continue to `LSF v10`.

## Current Pivot State

- `LSF` is closed as an active synthesis route.
- The next route should use a new synthesis family rather than another
  `LSF` carrier retune.
- The most grounded next candidate is a vocoder-based carrier family, because
  `docs/80` already recorded that the `ATRR` design could remain viable under a
  tighter synthesis surface than `LSF`.
- The next work item is route-definition and first-prototype planning, not a
  broad sweep.
- The first follow-up prototype is now defined as an `ATRR` vocoder-bridge
  target export plus a future narrow carrier adapter.
- The target-export stage is already implemented and has produced fixed8 target
  packages under `artifacts/diagnostics/atrr_vocoder_bridge_target_export/`.
- The first narrow carrier adapter is now implemented and has been run on the
  fixed8 target packages.
- Current adapter backend: `griffinlim_mel_probe`.
- Current reading: adapter boundary is validated, but backend quality is still
  blocked by weak `F0` preservation.
- A first local `F0`-aware neural backend has now also been tested through a
  local `RVC` posterior bridge.
- That local `RVC` bridge is rejected as a route candidate because it regressed
  on target shift, loudness drift, and `F0` drift versus the bounded
  Griffin-Lim probe.
- A first true mel-native neural vocoder backend has now also been tested via
  `torchaudio WaveRNN`.
- The adapter now supports backend-domain mel reconstruction for external
  mel-native backends, and this is required for future backend judgments.
- Even after backend-domain adaptation, `WaveRNN` is rejected for the active
  route because pitch preservation is catastrophically weak.
- A direct `SpeechT5HifiGan` integration attempt was blocked by repeated
  `huggingface.co` fetch timeouts in this environment.
- A local `Vocos mel 24khz` backend has now also been tested after backend-bin
  adaptation and is rejected because source reconstruction and pitch stability
  are both too weak.
- Two local `BigVGAN` checkpoints have now also been tested.
- The current provisional best backend is
  `external_models/bigvgan_v2_22khz_80band_256x/` with explicit RMS matching.
- A bounded post-vocoder median-`F0` correction layer has now also been tested
  on top of that backend.
- The best bounded setting currently uses a `150` cent trigger and a `300` cent
  correction cap.
- That mitigation materially improves average `F0` drift and targetward movement
  versus the plain backend, but it also raises mel reconstruction error and
  still leaves `VCTK` weaker than `LibriTTS`.
- A focused weak-row diagnostics pass now shows the remaining `VCTK` failures
  split into two classes:
  weak target packages and backend-instability rows.
- `p241_005_mic1` is the clearest backend-instability row still worth trying to
  save.
- The stack is therefore still machine-only even though it is now stronger than
  the plain backend.
- The next carrier task is therefore not another local `RVC` bridge variant,
  not generic `WaveRNN`, and not `Vocos`.
- The next carrier task is a narrow `VCTK`-focused BigVGAN diagnostics pass
  that explains the remaining weak rows before any human review.

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
- `docs/82_post_lsf_v8_review_and_conditioned_priors_pivot_v1.md`
- `docs/83_conditioned_lsf_v9_machine_sweep_v1.md`
- `docs/84_v9_sample_drift_invalidation_and_fixed8_review_policy_v1.md`
- `docs/85_lsf_route_closure_and_vocoder_pivot_prep_v1.md`
- `docs/86_new_carrier_requirements_and_first_vocoder_bridge_prototype_v1.md`
- `docs/87_vocoder_carrier_adapter_probe_v1.md`
- `docs/88_local_rvc_posterior_bridge_probe_rejected_v1.md`
- `docs/89_torchaudio_wavernn_domain_adapt_probe_rejected_v1.md`
- `docs/90_local_bigvgan_probe_and_vocos_rejection_v1.md`
- `docs/91_bigvgan_bounded_pitch_correction_probe_v1.md`
- `docs/92_vctk_bigvgan_weak_row_diagnostics_v1.md`
- `experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v8.json`
- `experiments/stage0_baseline/v1_full/speech_lsf_fixed_review_manifest_v8.csv`
- `artifacts/listening_review/stage0_speech_lsf_listening_pack/v8/`
- `artifacts/diagnostics/lsf_v8_review_f0_summary/`
- `artifacts/machine_gate/lsf_v8/`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9/`
- `experiments/stage0_baseline/v1_full/lsf_machine_sweep_v9_fixed8/`
- `artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9/`
- `artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/`
- `artifacts/listening_review_rollup/lsf_v9_fixed8_v9a/`
- `artifacts/machine_gate/lsf_v9_fixed8_v9a/`
- `scripts/run_lsf_machine_sweep.py`
- `scripts/build_stage0_speech_lsf_listening_pack.py`
- `scripts/summarize_lsf_review_by_f0.py`
- `scripts/export_atrr_vocoder_bridge_targets.py`
- `scripts/run_atrr_vocoder_carrier_adapter.py`
- `artifacts/diagnostics/atrr_vocoder_bridge_target_export/v1_fixed8_v9a/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_gl_probe/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_rvc_bridge/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_wavernn_domainadapt_smoke2/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_vocos_smoke2/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_rmsmatch_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_rmsmatch_pitchcorr150_cap300_full8/`

## Next Allowed Action

The next action is to continue the new synthesis-family route:

1. freeze the `LSF` route as closed
2. keep the fixed8 comparison manifest as the human baseline
3. use the exported `ATRR` target packages as the front half of the new route
4. keep the current adapter machine-only and do not send it to human review
5. keep the local `RVC` posterior bridge rejected as a direct carrier candidate
6. keep generic `WaveRNN` rejected as a direct carrier candidate
7. preserve backend-domain mel reconstruction as a required adapter step
8. keep `external_models/bigvgan_v2_22khz_80band_256x/` as the active backend
9. keep bounded pitch correction as the current best mitigation shape
10. prioritize backend-stability diagnostics on `p241_005_mic1`
11. do not expect backend-only fixes to rescue the weakest package-limited rows
12. rerun machine probe before any new broad sweep or human pass
