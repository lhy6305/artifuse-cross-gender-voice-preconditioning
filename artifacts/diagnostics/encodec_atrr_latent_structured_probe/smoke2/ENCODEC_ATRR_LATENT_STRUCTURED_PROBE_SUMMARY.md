# Encodec ATRR Latent Structured Probe Summary v1

- rows: `2`
- sample_rate: `24000`
- device: `cuda`
- bandwidth_kbps: `24.0`
- avg target_logmel_delta_l1_db: `0.1017`
- avg target_delta_rms: `0.0087`
- avg context_delta_rms: `0.0023`
- avg total_delta_rms: `0.0093`
- avg target_core_mel_loss: `0.004543`
- avg target_offcore_energy: `0.000150`
- avg final_core_mel_loss: `0.004038`
- avg final_offcore_energy: `0.000178`
- avg final_wave_l1: `0.000374`
- avg core_mask_ratio: `0.0500`

## Strongest Target Movers

- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | target_rms=`0.009406` | core_loss=`0.004538`
- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | target_rms=`0.008087` | core_loss=`0.003538`

## Strongest Context Compensators

- `libritts_r__1995__1995_1826_000022_000000__82d5a66723` | context_rms=`0.002725` | offcore_energy=`0.000218`
- `libritts_r__1919__1919_142785_000089_000003__11e66c65d9` | context_rms=`0.001805` | offcore_energy=`0.000138`
