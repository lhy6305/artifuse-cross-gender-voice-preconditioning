# Second ATRR Row Targeted Human Pack Ready v1

## Summary

This checkpoint records the second fixed8 human-review pack for the ATRR
BigVGAN route.

The pack is built from the promoted row-targeted machine baseline:

- `v1_fixed8_v9a_bigvgan_11025_hybrid_rowveto_p230_rowoverride_2086_025_full8`

Output:

- `artifacts/listening_review/stage0_atrr_vocoder_bigvgan_fixed8/rowveto_p230_override2086_025_v1/`

## Pack Identity

- pack label: `bigvgan_rowveto_p230_override2086_025_v1`
- rows: `8`
- originals copied: `8`
- processed files copied: `8`

Core files:

- `listening_review_queue.csv`
- `listening_pack_summary.csv`
- `listening_review_quant_summary.md`
- `README.md`

## Important Interpretation Rule

This pack contains one explicit control row:

- `p230_107_mic1`

That row is intentionally vetoed and is expected to behave like a source-anchor
control row rather than a transformed-row success.

This caveat is recorded in two places:

- `README.md`
- `listening_review_queue.csv` through `auto_quant_notes=control_row_source_anchor`

## Build Path

The pack was built with:

- `scripts/build_atrr_vocoder_human_review_pack.py`

New script support added for this pack:

- extra pack-level README notes
- explicit control-row annotation in queue output

## Route Decision

- Keep the promoted row-targeted stack as the active machine baseline.
- Use this pack as the next human-review entry point.

## Immediate Next Step

Run fixed8 human review on:

- `artifacts/listening_review/stage0_atrr_vocoder_bigvgan_fixed8/rowveto_p230_override2086_025_v1/listening_review_queue.csv`

Human interpretation rule:

- judge transformed-row audibility and structural safety separately from the
  `p230` control row
