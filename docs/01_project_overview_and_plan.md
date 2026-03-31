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
- A single-row cap sweep on `p241_005_mic1` now shows that post-vocoder
  correction-cap tuning is not monotonic on that row.
- The next stabilization idea should therefore change the correction shape, not
  just tune nearby cap values.
- A voiced-only pre-vocoder target-log-mel blend has now been tested as that
  shape change.
- The resulting full8 stack is now the best machine result on the active route:
  stronger targetward movement than the previous bounded-cap stack, materially
  lower mel error, and still controlled pitch drift.
- The active stack is now a machine-credible candidate for the first human
  review on the new synthesis-family route.
- The first fixed8 human pack for that stack is now built and smoke-validated.
- That first human review is now complete.
- Human result: reject the current carrier stack because all reviewed rows show
  audible structural distortion and the output sounds mechanically synthesized
  enough to block resonance judgment.
- The route is not fully closed from that result alone, because the failure mode
  is structure preservation, not necessarily target representation invalidity.
- A new structure-focused quantitative audit is now implemented and run through
  `scripts/audit_speech_structure_from_queue.py`.
- That audit shows the current ATRR vocoder pack is structurally much farther
  from the source than the old fixed8 `LSF v9a` pack.
- A second structure-first audit path is now implemented through
  `scripts/audit_atrr_vocoder_carrier_summary.py`.
- That split audit shows the current BigVGAN stack adds some carrier-only
  distortion, but the larger jump happens after the ATRR edit is injected into
  the carrier input.
- The adapter now supports a new pre-vocoder
  `frame_distribution_anchor_alpha` control for stronger source anchoring at
  the edited-frame stage.
- A narrow fixed8 anchor sweep has now been run on top of the BigVGAN stack.
- The best pack-level tradeoff in that sweep is
  `frame_distribution_anchor_alpha = 0.75` plus the older
  `voiced_target_blend_alpha = 0.75`.
- That `anchor075` stack improves both target shift and structure metrics versus
  the previously reviewed BigVGAN stack, but structure is still not clean enough
  for another human review.
- Stronger anchoring is also not monotonic at row level: `anchor050` and
  `anchor0625` reduce average structure risk further but collapse
  `p241_005_mic1`.
- A follow-up selective frame-anchor sweep has now also been tested on top of
  `anchor075`.
- That selective control slightly lowers average structure risk, but the gain is
  too small for the amount of shift it gives back.
- It also collapses `p230_107_mic1` before that row becomes structurally safe.
- A dedicated `p230_107_mic1` single-row pitch-rescue probe has now also been
  tested with stronger post-vocoder correction.
- That backend-side pitch rescue also fails: stronger correction reduces shift
  to near zero before structure risk becomes acceptable.
- The next route step has now moved upstream into target-side bin gating before
  carrier synthesis.
- This target-side gate is the first post-human-review control that materially
  reduces structure risk without collapsing the entire pack.
- A global sweep showed that bin-gating thresholds are direction-sensitive.
- The current best machine-only stack now uses a direction-conditioned hybrid
  threshold:
  masculine delta `0.010`, feminine delta `0.015`, occupancy `0.05`.
- This hybrid stack improves pack-level target probe structure risk from
  `45.76` to `36.40` while keeping average shift at `41.65`.
- It is not ready for human review yet, but it replaces plain `anchor075` as
  the active machine baseline.
- A follow-up utterance-level strength-conditioned extension has now also been
  tested on top of that hybrid baseline.
- That strength-conditioned override regresses the pack slightly and does not
  improve the remaining high-risk rows in a useful way.
- So the hybrid target-bin gate remains the active machine baseline.
- A first `f0` conditioned refinement pass has now also been tested on top of
  the hybrid baseline.
- Tightening `masculine mid_f0` gives only a small structure gain while hurting
  `p230_107_mic1`, and tightening `feminine high_f0` harms `p241_005_mic1`.
- So none of the tested `f0` conditioned variants replace the current hybrid
  baseline.
- A first target-shape-conditioned override has now also been tested on top of
  the hybrid baseline.
- It is selective enough to touch the `2086` outlier without harming `p241`,
  but the gain is too small to justify a new baseline.
- A first row-targeted target-side control has now also been tested on top of
  the hybrid baseline.
- The strongest result so far uses a record-level veto for `p230_107_mic1` plus
  a record-level override `2086_149214_000006_000002=0.025`.
- This row-targeted stack improves average target probe structure risk from
  `36.40` to `31.01` and edit-added structure risk from `15.26` to `9.87`,
  while also raising average shift from `41.65` to `42.91`.
- The route caveat is explicit: `p230_107_mic1` is now effectively source
  passthrough and must be interpreted as a source-anchor control row rather than
  as a transformed-row success.
- This row-targeted stack now replaces the hybrid-only stack as the active
  machine baseline for the ATRR BigVGAN route.
- The second fixed8 human review pack for this promoted candidate is now built
  at `artifacts/listening_review/stage0_atrr_vocoder_bigvgan_fixed8/rowveto_p230_override2086_025_v1/`.
- That pack carries the `p230_107_mic1` control-row caveat in both the README
  and the queue metadata.
- The next carrier task is therefore not another local `RVC` bridge variant,
  not generic `WaveRNN`, and not `Vocos`.
- The immediate next action is to run human review on the new row-targeted
  fixed8 pack.

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
- `docs/93_p241_single_row_cap_sweep_nonmonotonicity_v1.md`
- `docs/94_bigvgan_pre_vocoder_voiced_blend_full8_probe_v1.md`
- `docs/95_first_atrr_vocoder_human_pack_ready_v1.md`
- `docs/96_atrr_first_human_review_structural_distortion_reject_and_structure_audit_v1.md`
- `docs/97_bigvgan_structure_first_anchor_sweep_v1.md`
- `docs/98_selective_anchor_and_p230_pitch_rescue_fail_v1.md`
- `docs/99_target_side_bin_gating_probe_v1.md`
- `docs/100_strength_conditioned_bin_gate_rejected_v1.md`
- `docs/101_f0_conditioned_bin_gate_probe_v1.md`
- `docs/102_shape_conditioned_gate_probe_v1.md`
- `docs/103_row_targeted_gate_baseline_and_second_human_pack_prep_v1.md`
- `docs/104_second_atrr_row_targeted_human_pack_ready_v1.md`
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
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8/`
- `artifacts/listening_review/stage0_atrr_vocoder_bigvgan_fixed8/blend075_pc150_cap200_v1/`
- `scripts/build_atrr_vocoder_human_review_pack.py`
- `scripts/audit_speech_structure_from_queue.py`
- `scripts/audit_atrr_vocoder_carrier_summary.py`
- `artifacts/diagnostics/speech_structure_audit/v1/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v1_baseline_split/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v3_anchor_sweep_plus0625/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v4_selective_anchor_sweep/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/p230_pitch_diag/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v6_target_bin_gating_sweep_plus010/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v7_target_bin_gating_hybrid/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v8_strength_conditioned_bin_gate/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v9_f0_conditioned_bin_gate_sweep/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v10_shape_conditioned_gate/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_anchor075_blend075_pc150_cap200_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_anchor075_binmask_hybrid_m010_f015_occ005_blend075_pc150_cap200_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_binmask_hybrid_strengthcut035_m010_f015_weakm015_weakf005_occ005_blend075_pc150_cap200_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_hybrid_f0_mmid015_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_hybrid_f0_fhigh020_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_hybrid_f0_mmid015_fhigh020_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_hybrid_shape_top3_042_fsharp020_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_hybrid_shape_top3_045_fsharp020_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_hybrid_rowveto_p230_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_hybrid_rowveto_p230_rowoverride_2086_020_full8/`
- `artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_hybrid_rowveto_p230_rowoverride_2086_025_full8/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v11_row_targeted_gate/`
- `artifacts/diagnostics/atrr_carrier_structure_audit/v12_row_targeted_gate_plus2086_025/`
- `artifacts/listening_review/stage0_atrr_vocoder_bigvgan_fixed8/rowveto_p230_override2086_025_v1/`

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
9. reject the current voiced-blend BigVGAN stack for human-use continuation
10. keep the ATRR target package family open
11. require both target-shift metrics and structure audit before the next human
    review
12. use `anchor075` as the new machine-only BigVGAN baseline
13. do not expect backend-only fixes to rescue the weakest package-limited rows
14. do not assume stronger source anchoring is monotonic at row level
15. move the next stabilization pass upstream into target-side selective gating
16. use the row-targeted BigVGAN baseline with `p230` veto plus `2086=0.025`
    override as the active machine-only stack
17. when this stack goes to human review, interpret `p230_107_mic1` as a
    source-anchor control row rather than as a transformed-row success
18. use the already built fixed8 pack
    `stage0_atrr_vocoder_bigvgan_fixed8/rowveto_p230_override2086_025_v1/`
    as the next human-review entry point
