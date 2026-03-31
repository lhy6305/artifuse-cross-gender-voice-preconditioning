# ATRR First Human Review Structural Distortion Reject And Structure Audit v1

## Summary

This checkpoint records the first human review result for the active ATRR
vocoder route and the follow-up structure-focused quantitative audit.

The pack under review was:

- `artifacts/listening_review/stage0_atrr_vocoder_bigvgan_fixed8/blend075_pc150_cap200_v1/`

The human result rejects the current carrier stack for listening use.

But it does not by itself reject the ATRR target representation.

## Human Review Result

Review outcome from the completed queue:

- reviewed: `8/8`
- effect audible: `yes=6`, `no=2`
- artifact issue: `yes=8`
- keep recommendation: `no=7`, `n/a=1`

Rollup:

- `artifacts/listening_review_rollup/v1/LISTENING_REVIEW_ROLLUP.md`

User-level reading:

- the outputs sound mechanically synthesized or like a novelty voice filter
- utterance structure is audibly warped
- resonance movement can no longer be judged reliably on top of the structural
  distortion

This means the current stack is rejected as a human-review-worthy carrier.

## Why The Route Is Not Fully Rejected

This human result is different from the old `LSF` route failure mode.

The old `LSF` route mostly failed because the effect was too weak or moved the
wrong spectral impression.

The current ATRR vocoder result fails because the carrier output itself is
structurally distorted enough to block judgment of the target resonance move.

So the correct interpretation is:

- reject the current carrier stack
- do not yet reject the ATRR target package family

## New Quantitative Audit

To quantify this failure mode directly, a new structure-focused audit was added:

- `scripts/audit_speech_structure_from_queue.py`

This audit measures source-to-processed structural distortion rather than
targetward movement.

It was run on:

1. the current ATRR vocoder human pack
2. the old fixed8 `LSF v9a` pack for context

Outputs:

- `artifacts/diagnostics/speech_structure_audit/v1/SPEECH_STRUCTURE_AUDIT.md`
- `artifacts/diagnostics/speech_structure_audit/v1/speech_structure_pack_audit.csv`
- `artifacts/diagnostics/speech_structure_audit/v1/speech_structure_row_audit.csv`

## Main Quantitative Finding

Current ATRR vocoder pack:

- avg logmel DTW L1: `1.7401`
- avg voiced overlap IoU: `0.5996`
- avg `F0` overlap MAE: `255.1232` cents
- avg structure risk score: `58.03`

Old fixed8 `LSF v9a` pack:

- avg logmel DTW L1: `0.3257`
- avg voiced overlap IoU: `0.9453`
- avg `F0` overlap MAE: `6.3389` cents
- avg structure risk score: `12.37`

Reading:

- the current ATRR vocoder stack is structurally much farther from the source
  than the old weak-`LSF` control
- this supports the user's mechanical-filter listening impression directly
- the main blocker is now structure preservation, not lack of a measurable edit

## Route Decision

- Reject the current BigVGAN voiced-blend carrier stack for human-use
  continuation.
- Do not close the ATRR target package family yet.
- Treat structure preservation as the primary blocker on the active route.

## New Process Rule

For future carrier experiments on this route:

1. run machine target-shift metrics
2. run structure audit
3. send to human review only if both are acceptable

This avoids repeating a human pass on outputs whose structure is already too
distorted to judge resonance movement.

## Immediate Next Step

The next route step should look for a carrier or carrier constraint that keeps
the ATRR target package family but reduces source-structure distortion
materially before the next human review.
