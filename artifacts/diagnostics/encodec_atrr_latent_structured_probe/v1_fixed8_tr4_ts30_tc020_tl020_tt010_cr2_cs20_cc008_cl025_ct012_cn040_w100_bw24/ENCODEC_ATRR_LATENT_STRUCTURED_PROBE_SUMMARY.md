# Encodec ATRR Latent Structured Probe Summary v1

- rows: `8`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- avg target_logmel_delta_l1_db: `0.0678`
- avg target_delta_rms: `0.0080`
- avg context_delta_rms: `0.0020`
- avg total_delta_rms: `0.0084`
- avg target_core_mel_loss: `0.004559`
- avg target_offcore_energy: `0.000121`
- avg final_core_mel_loss: `0.004086`
- avg final_offcore_energy: `0.000128`
- avg final_wave_l1: `0.000338`
- avg core_mask_ratio: `0.0609`

## Strongest Target Movers

- `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7` | target_rms=`0.010151` | core_loss=`0.004256`
- `libritts_r__174__174_50561_000024_000000__d665dc2840` | target_rms=`0.010054` | core_loss=`0.005871`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | target_rms=`0.009406` | core_loss=`0.004538`

## Strongest Context Compensators

- `libritts_r__174__174_50561_000024_000000__d665dc2840` | context_rms=`0.003081` | offcore_energy=`0.000116`
- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | context_rms=`0.002725` | offcore_energy=`0.000218`
- `libritts_r__2086__2086_149214_000006_000002__23f1c25eb7` | context_rms=`0.002552` | offcore_energy=`0.000145`
