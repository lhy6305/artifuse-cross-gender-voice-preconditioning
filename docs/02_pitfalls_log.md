# Pitfalls Log

## Active Global Pitfalls

### 1. PowerShell reads are unsafe without explicit UTF-8

- Problem: PowerShell may decode UTF-8 text through the local code page if encoding is not specified.
- Impact: correct files may appear garbled and may be edited incorrectly afterward.
- Rule: always read repo text with explicit UTF-8.

### 2. PowerShell text writes are not trusted for repo docs

- Problem: PowerShell UTF-8 text writes may add a BOM in this environment.
- Impact: active docs may gain noisy headers and inconsistent byte format.
- Rule: do not use PowerShell text write cmdlets for repo doc edits.

### 3. Active docs and user replies follow different language rules

- Problem: the user works in Chinese, while active docs must stay English ASCII.
- Impact: doc maintenance can drift into the wrong language unless the two channels stay separate.
- Rule: keep active docs in English ASCII, and keep user-facing replies in Simplified Chinese.

### 4. Heavy local assets and local work dirs must stay outside Git

- Problem: model weights, indexes, raw audio, dataset archives, and local work dirs are easy to stage by accident.
- Impact: Git history can become heavy, noisy, or unsafe.
- Rule: keep those assets ignored by default and keep only lightweight recoverable artifacts in Git.

### 5. Use stable `record_id`, not `utt_id` or `rule_id`, for joins

- Problem: `utt_id` is not globally unique in the full manifest, and `rule_id`
  is a candidate-level label reused across multiple rows in a pack.
- Impact: cache joins, resume logic, and output file naming can silently
  misalign records or overwrite artifacts.
- Rule: use stable `record_id` for joins, cache keys, and resume logic.
  Use `record_id` plus `utt_id` for row-level artifact names when needed.

### 6. Use repo root `.\python.exe` for project scripts

- Problem: mixing in system Python can break local import assumptions and runtime consistency.
- Impact: build and analysis scripts may fail or drift across sessions.
- Rule: use repo root `.\python.exe` unless a task explicitly documents a different interpreter.

### 7. PowerShell inline Python patch scripts fail with nested quotes

- Problem: PowerShell `-c "..."` inline strings mangle nested double quotes and produce SyntaxError.
- Impact: patch scripts written inline fail before running any code.
- Rule: write patch scripts to a file using `[System.IO.File]::WriteAllText(path, content, UTF8)`,
  then run them as a separate step with `.\python.exe .\tmp\patch_name.py`.

### 8. LPC fit objective must use utterance-level prototype, not per-frame ATRR target

- Problem: comparing LPC carrier envelope against per-frame ATRR mel target distributions fails
  because LPC produces smooth envelopes while mel ATRR targets have sharp per-frame structure.
  The fit objective can never improve on the original and no frames are accepted.
- Impact: near-zero fit success rate, reconstruction produces no audible change.
- Rule: use the utterance-level weighted target-gender prototype as the fit objective target.
  Per-frame ATRR targets are for edit direction only, not for acceptance testing.

### 9. Highband error weight in LSF fit objective must be small

- Problem: the highband log-power error term is on the order of 0.29 to 0.35 per frame for
  the feminine direction (which legitimately raises energy). A weight of 0.08 adds 0.024 to
  0.028 to the objective per frame, wiping out fit+core improvement and rejecting valid edits.
- Impact: near-zero fit success rate for the feminine direction.
- Rule: keep the highband penalty weight at 0.005 or lower in the LSF fit objective.
  Highband preservation is already handled through the synthesis blend path.

### 10. mel distribution local_strength normalization must be relative, not absolute

- Problem: using a hardcoded absolute divisor (e.g. 0.12) for local_strength when distributions
  sum to 1.0 across 80 bins produces near-zero strength values (actual slice deltas are 0.001 to 0.03).
- Impact: all dynamic edits collapse to near-identity, zero audible change.
- Rule: normalize local_strength by the maximum possible mass for the slice
  (slice bin count / total bins) rather than a hardcoded constant.

### 11. Human comparison packs must keep a stable listening set across rounds

- Problem: changing the human listening pack sample set mid-series changes both
  the method and the evaluation set at the same time.
- Impact: cross-round listening conclusions become non-comparable and can look
  like a user mistake even when the pack itself drifted.
- Rule: once a human comparison track starts, freeze the listening set through
  an explicit manifest until a deliberate review-set reset is declared.

### 12. External vocoder backends must use their own mel frontend domain

- Problem: exported target packages currently store project-domain mel objects,
  but external neural vocoders are often trained on a different mel frontend
  with different sample rate, hop length, window length, and mel limits.
- Impact: feeding project-domain `target_log_mel` directly into a backend can
  produce false-negative results that look like a backend failure but are
  actually frontend-domain mismatch.
- Rule: before judging an external mel-native backend, rebuild source and target
  mel in that backend's own frontend domain, then run the carrier probe.

### 13. HuggingFace-hosted backend fetches may time out in this environment

- Problem: model downloads from `huggingface.co` can time out repeatedly here,
  even when other hosts such as `download.pytorch.org` still work.
- Impact: a backend integration attempt can fail before any model code runs.
- Rule: treat repeated HuggingFace fetch timeout as an environment access issue,
  not as proof that the backend API is unusable.

### 14. External backend mel bin counts may differ from exported frame edits

- Problem: exported target packages currently store frame-level edited
  distributions in the project mel dimension, but external backends can require
  a different mel bin count.
- Impact: direct reuse of frame edits can fail at runtime or silently distort
  the rebuilt backend-domain target mel.
- Rule: when rebuilding backend-domain target mel, resample edited frame
  distributions into the backend mel bin count before per-frame energy restore.

### 15. Unbounded post-vocoder pitch correction can destroy weak rows

- Problem: a full median-`F0` correction step after backend synthesis can
  reduce average pitch drift but over-correct already unstable rows.
- Impact: some weak rows can collapse to near-zero target shift even though the
  average `F0` metric looks better.
- Rule: if post-vocoder pitch correction is used on this route, keep it bounded
  with both a drift trigger and a correction cap.

### 16. Weak-row cap sweeps can be nonmonotonic

- Problem: on unstable rows such as `p241_005_mic1`, nearby correction-cap
  values can produce sharply different outcomes instead of a smooth tradeoff.
- Impact: blind local cap sweeps can waste route budget and create false
  confidence that a nearby cap will fix the row.
- Rule: once cap behavior is visibly nonmonotonic on a weak row, stop nearby
  cap tuning and switch to a different stabilization shape.

### 17. Target-shift metrics can miss carrier-level structural collapse

- Problem: a carrier stack can look targetward on the active machine metrics
  while still warping speech structure enough to sound mechanical or novelty
  filtered.
- Impact: human review can become unable to judge resonance movement at all,
  even if target-shift metrics looked promising.
- Rule: for carrier-family experiments, do not rely on target-shift metrics
  alone. Run a source-to-processed structure audit before sending a pack to
  human review.

### 18. Stronger source anchoring is not monotonic at row level

- Problem: pack-level source-anchoring sweeps can reduce average structure risk
  while collapsing individual rescued rows.
- Impact: a setting can look safer in the aggregate and still destroy the route
  on specific rows such as `p241_005_mic1`.
- Rule: for ATRR carrier tuning, do not accept a stronger anchor setting from
  pack averages alone. Check row-level targetward movement and structure risk in
  the same pass.

### 19. Stronger backend-side pitch rescue can collapse weak rows before structure improves

- Problem: on remaining weak rows such as `p230_107_mic1`, increasing
  post-vocoder pitch correction can reduce measured pitch drift while also
  erasing targetward movement.
- Impact: the row can look closer in pitch and still remain structurally unsafe,
  producing no useful route progress.
- Rule: do not treat stronger backend-side pitch rescue as the default next move
  for weak ATRR BigVGAN rows. If a row already loses shift under stronger pitch
  correction, move upstream to target-side selective gating instead.

### 20. Target-side edit gates can be direction-sensitive

- Problem: one global target-side bin-gating threshold can improve pack-level
  structure risk while still over-suppressing one edit direction.
- Impact: a global gate can hide a better direction-conditioned tradeoff and
  make the route look flatter than it really is.
- Rule: when target-side gating shows meaningful pack-level improvement, check
  whether the best threshold differs by direction before freezing the baseline.

### 21. Scalar source-target strength alone is too weak for the next target-side gate split

- Problem: a simple weak-package override keyed only to utterance-level
  source-target `EMD` does not separate the remaining bad rows cleanly enough.
- Impact: the override can regress the pack while failing to improve the rows
  it was supposed to rescue.
- Rule: do not assume that scalar source-target strength is the next best split
  after direction-conditioned gating. Prefer richer target-shape or `f0`
  conditioned splits next.

### 22. Whole-bucket f0 overrides can still be too blunt

- Problem: a bucket-level threshold override can improve pack averages while
  damaging a rescued row inside that same bucket.
- Impact: a seemingly cleaner `f0` split can still be a route regression once
  the key rows are inspected.
- Rule: after a direction-conditioned gate is active, do not promote a whole
  `f0` bucket override unless the main outlier rows also improve.

### 23. A selective shape override can be real and still too small to matter

- Problem: a target-shape-conditioned override can improve exactly the intended
  row while leaving the pack nearly unchanged.
- Impact: it is easy to overvalue a technically correct but practically tiny
  refinement.
- Rule: do not promote a shape-conditioned gate unless its row-level gain is
  large enough to change the pack-level tradeoff materially.

### 24. A row-level veto can improve the pack by becoming a control row

- Problem: a record-level veto can produce a large pack-level structure gain by
  turning a bad edit into near source passthrough.
- Impact: the pack can look materially better while containing fewer truly
  active edited rows than before.
- Rule: if a promoted stack uses a row-level veto, document that row explicitly
  as a control row and do not interpret its safety as an edited-row success.

### 25. Better structure metrics alone do not guarantee usable resonance judgment

- Problem: a carrier stack can cut structure-risk scores substantially and still
  sound obviously synthetic enough that core-resonance movement remains
  unjudgeable on most rows.
- Impact: a route can look materially improved in machine audits while still
  failing the real listening goal.
- Rule: after a structural improvement reaches human review, judge not only
  whether change is audible but also whether core resonance becomes
  interpretable. If artifacts still dominate perception, stop local tuning on
  that carrier family.

### 26. After a carrier-family rejection, screen source roundtrip first

- Problem: it is easy to jump straight into a new edit-injection design without
  checking whether the candidate carrier family itself has a high enough
  structure-preservation ceiling.
- Impact: route effort can be wasted on edit logic inside a carrier family that
  is already too lossy for the listening goal.
- Rule: after a human-reviewed carrier family is rejected for structural
  distortion, run a source-only roundtrip probe on the next candidate family
  before attempting ATRR edit injection.

### 27. Compare injected variants against the carrier roundtrip baseline

- Problem: a source-preserving carrier family can already shift the active
  targetward metric slightly even before any intended ATRR edit is injected.
- Impact: an injected prototype can look active while adding only trivial
  targetward gain over the plain carrier roundtrip baseline.
- Rule: for source-preserving carrier pivots, do not judge the first injected
  prototype in isolation. It must beat the carrier roundtrip baseline by a
  meaningful margin, not just remain cleaner than the previously rejected
  family.

### 28. A tighter mel-residual mask can still be too weak to justify the surface

- Problem: narrowing a mel-domain residual to a strict ATRR core-support mask
  can reduce structure cost, but it may also shrink the effective edit support
  to a very small fraction of bins.
- Impact: the new variant can look cleaner than the previous mel-residual
  version while still failing to beat the plain carrier roundtrip baseline by a
  meaningful margin.
- Rule: if a masked mel-residual variant only improves the tradeoff slightly
  and still stays near the roundtrip targetward baseline, close the whole
  mel-residual surface and move to a narrower injection boundary instead of
  continuing scalar mask tuning.

### 29. A low-order filter-side envelope can still regress below the roundtrip ceiling

- Problem: moving from a mel-domain residual to a narrower low-order
  filter-side envelope can reduce the apparent edit surface while also giving
  back targetward movement to below the plain carrier roundtrip baseline.
- Impact: the route can spend time on a seemingly more principled narrow
  surface that is still not a useful ATRR carrier.
- Rule: if a filter-side envelope variant stays above the roundtrip structure
  ceiling and also falls below the roundtrip targetward baseline, close the
  whole filter-side scalar-tuning surface and move to a true latent-side or
  code-side boundary.

### 30. Encodec decoder backward can fail through cuDNN RNNs in eval mode

- Problem: a latent-side optimization loop that backpropagates through the
  `Encodec` decoder on `CUDA` can hit `RuntimeError: cudnn RNN backward can
  only be called in training mode` when the model stays in `eval` mode.
- Impact: the first latent-side probe can fail before any optimization result
  is produced, even though the forward path itself is valid.
- Rule: for gradient-based latent or code-side probes through the `Encodec`
  decoder, disable cuDNN on the decoder forward path or use another equivalent
  decoder-call path that avoids the eval-mode cuDNN RNN backward restriction.

### 31. Bilinear low-rank latent factors cannot both start at exact zero

- Problem: a latent delta parameterized as `A @ B` has zero gradient on both
  factors when both `A` and `B` are initialized to exact zero.
- Impact: the optimization loop can appear to run normally while producing an
  exact-zero latent edit, exact-zero waveform drift, and a false impression
  that the surface is intrinsically too weak.
- Rule: when using bilinear low-rank latent or code-side factors, initialize
  both factors with small non-zero noise so gradient flow exists from the first
  step.

### 32. A hard native code refit can keep structure while losing the teacher gain

- Problem: projecting a good latent-side teacher back into a narrow native
  `Encodec` code slice through greedy hard refit can preserve structure while
  quantization error gives back too much targetward movement.
- Impact: a more natively discrete code-side boundary can look promising
  because it stays structurally clean, yet still fail to beat the active latent
  baseline on the actual route tradeoff.
- Rule: if a teacher-to-code refit stays near the latent structure floor but
  falls below the latent baseline on targetward shift, keep it as a comparison
  result and do not spend route budget on nearby retuning of the same refit
  surface.

### 33. A teacher-guided native shortlist can get close without clearing the latent baseline

- Problem: a code-side surface that uses a latent teacher only to define a
  target-aware native shortlist can raise targetward movement beyond older
  code-side designs while still failing to preserve quite as much structure as
  the latent baseline.
- Impact: the route can spend time on a more sophisticated native-code family
  that looks promising in one direction but still does not win the actual
  two-axis gate.
- Rule: if a teacher-guided shortlist code family comes close but does not beat
  the active latent baseline on both targetward shift and structure, record it
  as a comparison checkpoint and stop nearby retuning of the same shortlist
  surface.

### 34. A sparse native code gate can be cleaner than it is useful

- Problem: a very narrow gate between the base native code path and a
  teacher-derived native code path can keep waveform drift extremely small
  while also shrinking targetward movement back toward the weaker code-side
  results.
- Impact: a gate family can look disciplined and structurally safe without
  providing enough directional gain to justify replacing the latent baseline.
- Rule: if a sparse native code gate stays near the latent structure floor but
  falls back to roughly the old conservative code-side shift level, keep it as
  a comparison checkpoint and stop nearby retuning of that gate surface.

### 35. A hard native commit mask can trade away too much movement for tiny structural gain

- Problem: forcing code-side editing into a fully discrete base-versus-teacher
  commit mask can slightly improve structure while collapsing a large share of
  the targetward movement that the latent baseline already achieved.
- Impact: a very native and interpretable code surface can still fail the route
  because the structural gain is too small to pay for the directional loss.
- Rule: if a hard native commit family gains only a tiny structure margin while
  dropping far below the latent baseline on targetward shift, record it as a
  comparison checkpoint and stop nearby retuning of that discrete commit
  surface.

### 36. A small continuous repair on top of a hard native scaffold may not recover the teacher path

- Problem: adding a bounded low-rank residual correction on top of a hard
  native code scaffold can improve local mel fit while still failing to close
  the actual scaffold-to-teacher latent gap in a meaningful way.
- Impact: the route can spend another optimization stage on a more flexible
  hybrid surface that still underperforms both the active latent baseline and
  even the simpler hard-refit checkpoint on pack-level metrics.
- Rule: if a scaffold-plus-residual hybrid does not recover the latent teacher
  advantage and cannot even beat the plain hard-refit comparison, record it as
  a comparison checkpoint and stop nearby retuning of that hybrid surface.

### 37. Queue-relative distribution diagnostics need full prototype coverage

- Problem: `extract_resonance_distribution_diagnostics.py` builds each
  target-gender prototype from the same queue being scored. Small smoke
  subsets can drop the needed opposite-source-gender rows for a
  `(group_value, target_direction)` pair.
- Impact: a subset run can fail with `KeyError` or produce a non-comparable
  partial read even though the processed audio itself is valid.
- Rule: run queue-relative distribution diagnostics on the full comparison
  queue, or keep subset sampling balanced enough that every scored group still
  contains the required prototype pool for both source genders.

### 38. A soft time-frequency support map can get close without clearing the latent baseline

- Problem: replacing a flat binary latent support with a softer
  frame-distribution-weighted time-frequency support plus an off-support null
  penalty can slightly improve a few weak rows while causing equally small
  regressions on stronger rows.
- Impact: the new latent objective can look more targeted and still fail the
  actual pack gate because the net shift gain is too small and structure does
  not improve.
- Rule: if a soft support latent family only lands near-tied with `latent v1`,
  record it as a comparison checkpoint and do not spend route budget on nearby
  support-floor, blend, or null-weight retuning.

### 39. A direct distribution objective can improve weak rows while regressing the pack

- Problem: fitting edited frame distributions and utterance-level target
  distribution more directly can produce localized gains on a few weak rows
  while materially giving back targetward movement on stronger rows.
- Impact: the objective looks more aligned with the evaluation metric, yet the
  pack-level tradeoff can still regress because row-level gains and losses are
  redistributed unevenly.
- Rule: if a direct distribution-objective latent family improves a few weak
  rows but loses the pack-level gate versus `latent v1`, record it as a
  comparison checkpoint and do not spend route budget on nearby scale or weight
  retuning of that same family.

### 40. Frame-level distribution weights cannot reuse mel-bin support masks directly

- Problem: a hybrid latent objective can mix mel-bin support masks for
  masked delta-fit with frame-level gap weights for distribution losses.
  Multiplying those tensors directly crosses two different axes.
- Impact: the probe can fail at runtime with a shape mismatch, or worse, a
  silent broadcast bug can misweight the frame-level distribution objective.
- Rule: keep masked delta-fit weights in mel-bin x frame space, and build
  frame-level distribution weights separately in frame space only.

## Archived Historical Pitfalls

Historical and resolved setup-specific pitfalls were moved out of this active handoff file into:

- `docs/68_archive_historical_pitfalls_from_old_02_v1.md`
