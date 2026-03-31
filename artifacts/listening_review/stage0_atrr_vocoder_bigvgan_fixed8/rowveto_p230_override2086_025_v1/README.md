# ATRR Vocoder Human Review Pack bigvgan_rowveto_p230_override2086_025_v1

- purpose: `second fixed8 human pack for row-targeted ATRR BigVGAN baseline`
- rows: `8`

- note: `p230_107_mic1 is an intentional source-anchor control row in this pack`
- note: `interpret human conclusions on transformed rows separately from the p230 control row`

## Rebuild

```powershell
.\python.exe .\scripts\build_atrr_vocoder_human_review_pack.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --adapter-summary artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_hybrid_rowveto_p230_rowoverride_2086_025_full8/atrr_vocoder_carrier_adapter_summary.csv `
  --output-dir artifacts/listening_review/stage0_atrr_vocoder_bigvgan_fixed8/rowveto_p230_override2086_025_v1 `
  --pack-label bigvgan_rowveto_p230_override2086_025_v1 `
  --control-record-id vctk_corpus_0_92__p230__p230_107_mic1__8330d16640 `
  --pack-note p230_107_mic1 is an intentional source-anchor control row in this pack `
  --pack-note interpret human conclusions on transformed rows separately from the p230 control row `
  --pack-purpose "second fixed8 human pack for row-targeted ATRR BigVGAN baseline"
```
