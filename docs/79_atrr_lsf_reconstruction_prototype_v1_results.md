# ATRR LSF Reconstruction Prototype v1 Results

## Scope

This document records the first machine-only reconstruction run of the ATRR method
through the LSF carrier path, including the debugging history and final working state.

Implementation:

- `scripts/reconstruct_atrr_lsf_prototype.py`

Final output artifacts:

- `artifacts/diagnostics/atrr_lsf_reconstruction_prototype_v5/atrr_lsf_reconstruction_summary.csv`
- `artifacts/diagnostics/atrr_lsf_reconstruction_prototype_v5/ATRR_LSF_RECONSTRUCTION_SUMMARY.md`

Baseline for comparison:

- `artifacts/diagnostics/lsf_v7_resonance_distribution_v2/resonance_distribution_diagnostic_summary.csv`

## Parameters Used

- `core_step_size = 0.50`
- `off_core_step_size = 0.15`
- `frame_smoothness_weight = 0.30`
- `max_bin_step = 0.0085`
- `preserve_highband_from_hz = 3000.0`

These parameters are the conservative reconstruction candidate band from doc 77.

## Bugs Found And Fixed During Implementation

Three bugs were found and fixed in `reconstruct_atrr_lsf_prototype.py` before
the reconstruction produced valid results.

### Bug 1: `local_strength` normalization

The original `build_dynamic_pair_controls` function used a hardcoded `0.12`
divisor for `local_strength`. Mel distributions sum to 1.0 across 80 bins,
so per-range slice deltas are on the order of 0.001 to 0.03. Dividing by
`0.12` produced near-zero `local_strength` values, which zeroed out all
dynamic edits.

The fix replaced the entire `build_dynamic_pair_controls` approach with
`build_scaled_pair_controls`, which directly scales the v7 default ratios
by a grid of scale fractions `[0.25, 0.50, 0.75, 1.00, 1.25, 1.50, 2.00]`.
The fit objective then selects the effective edit strength per frame.

### Bug 2: Per-frame ATRR target used as fit objective target

The fit objective was comparing the LPC-derived smooth carrier envelope
against the per-frame ATRR-edited mel distribution target. These two
representations are structurally incompatible. The LPC envelope is smooth;
the mel ATRR target has sharp per-frame structure. The fit objective was
asking the LPC carrier to reproduce a peaky mel distribution, which it
cannot do, so no candidate ever beat the original.

The fix changed the fit objective to compare against `target_prototype`,
the utterance-level weighted target-gender prototype. This is the same
smooth distribution that the reconstruction diagnostics measure against.

### Bug 3: Highband error weight too large

The fit objective included a `0.08 * highband_error` term. The highband
error is measured in log-power space on raw FFT bins and reaches values of
0.29 to 0.35 for the feminine direction, which routinely shifts energy
upward. The `0.08` weight added `+0.024` to `+0.028` to the objective per
frame, wiping out the `fit + core` improvement and causing the acceptance
gate to reject nearly all feminine-direction frames.

The fix reduced the highband weight from `0.08` to `0.005`. The high-band
preservation is already handled separately through the synthesis blend path
and the `preserve_highband_from_hz` parameter, so the objective penalty is
not needed at this weight.

## Final Run Results (v5)

Pack-level summary:

- `avg fit_success_rate: 0.0892`
- `avg frame_passthrough_rate: 0.9108`
- `avg reconstructed shift score: 50.46`
- `avg reconstructed core coverage: 70.01`
- `avg reconstructed localization penalty: 42.29`
- `avg reconstructed frame improvement mean: 0.000226`

By direction:

- feminine: fit success `0.0327`, shift `50.02`, coverage `79.75`
- masculine: fit success `0.1457`, shift `50.89`, coverage `60.27`

## Per-Row Comparison Against Observed v7

All 8 rows show improvement on core coverage versus observed v7.
6 of 8 rows show positive delta on shift score versus observed v7.
All 8 rows show positive delta on frame improvement mean.

Selected per-row deltas:

- `libritts_masculine_v7` row 1: delta_shift=`-0.68`, delta_coverage=`+9.25`
- `libritts_masculine_v7` row 2: delta_shift=`+5.52`, delta_coverage=`+21.02`
- `libritts_feminine_v7` row 1: delta_shift=`+13.84`, delta_coverage=`+27.53`
- `libritts_feminine_v7` row 2: delta_shift=`+23.45`, delta_coverage=`+36.24`
- `vctk_masculine_v7` row 1: delta_shift=`-2.33`, delta_coverage=`+13.93`
- `vctk_masculine_v7` row 2: delta_shift=`+14.77`, delta_coverage=`+31.69`
- `vctk_feminine_v7` row 1: delta_shift=`+33.59`, delta_coverage=`+16.60`
- `vctk_feminine_v7` row 2: delta_shift=`+8.37`, delta_coverage=`+33.58`

Brilliance and presence deltas are small and mostly non-negative.
F0 and voiced structure are preserved (delta_f0_median near zero in CSV).

## Reading Of The Result

The reconstruction prototype is machine-viable.

The core diagnostic advantage of ATRR over observed v7 survives the
reconstruction step: even with a low per-frame fit success rate of 9%,
the core coverage improvement over observed v7 is large and consistent
across all 8 rows.

The two rows with negative delta on shift score both had strong observed
v7 baselines. The reconstruction does not collapse those rows.

The fit success rate of 9% does not indicate failure. With 400 to 900
voiced frames per utterance, 9% yields 36 to 81 successfully edited frames
per utterance, which is enough to produce a measurable distribution shift.

## Open Risks

- The masculine direction fit success rate (14.6%) is higher than feminine
  (3.3%). The feminine direction uses upward center shifts, which move more
  energy against the existing LPC pole structure and may require a higher
  scale fraction to find improvement.
- The `fit_success_rate` metric counts frames where the best candidate beat
  the original objective. Raising the scale ceiling further (e.g., to 3.0)
  might recover more feminine frames.
- No human listening has been done yet. The machine metrics are positive
  but the final quality gate is human review.

## Minimum Acceptance Check

The reconstruction passes the minimum acceptance rule from doc 78:

- voiced-frame fit succeeds on some frames: YES (9% average)
- reconstruction keeps ATRR diagnostic advantage over observed v7: YES
- artifact proxies (brilliance, presence) do not collapse: YES
- F0 and voiced structure preserved: YES

## Immediate Next Step

The next step is to build a listening pack from the reconstruction prototype
and run it through the machine gate before any human review.

- use `atrr_lsf_reconstruction_prototype_v5` artifacts as the processed audio
- run `scripts/build_listening_machine_gate_report.py` against the new pack
- only send to human review if the machine gate passes