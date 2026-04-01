# Encodec Roundtrip Probe v1

- purpose: `measure source-preserving carrier ceiling before ATRR edit injection`
- rows: `8`
- bandwidth_kbps: `24.0`
- repository: `torch hub cache`

## Rebuild

```powershell
.\python.exe .\scripts\run_encodec_roundtrip_probe.py `
  --template-queue artifacts/listening_review/stage0_speech_lsf_machine_sweep_v9_fixed8/split_core_focus_v9a/listening_review_queue.csv `
  --output-dir artifacts/diagnostics/encodec_roundtrip_probe/v1_fixed8_bw24 `
  --bandwidth 24.0
```
