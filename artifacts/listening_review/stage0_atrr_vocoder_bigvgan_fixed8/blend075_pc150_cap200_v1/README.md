# ATRR Vocoder Human Review Pack bigvgan_blend075_pc150_cap200_v1

- purpose: `first fixed8 human pack for voiced-blend BigVGAN carrier stack`
- rows: `8`

## Rebuild

```powershell
.\python.exe .\scripts\build_atrr_vocoder_human_review_pack.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --adapter-summary artifacts/diagnostics/atrr_vocoder_carrier_adapter/v1_fixed8_v9a_bigvgan_11025_blend075_pc150_cap200_full8/atrr_vocoder_carrier_adapter_summary.csv `
  --output-dir artifacts/listening_review/stage0_atrr_vocoder_bigvgan_fixed8/blend075_pc150_cap200_v1 `
  --pack-label bigvgan_blend075_pc150_cap200_v1
```
