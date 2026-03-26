# Stage 0 Band-Gain 原型 v1

## 当前产物

当前已经把候选规则进一步映射成 `prototype-only` 的 band-gain 配置：

- `experiments/stage0_baseline/v1_full/rule_candidate_band_gain_profiles_v1.csv`
- `experiments/stage0_baseline/v1_full/rule_candidate_band_gain_profiles_v1.json`

对应生成脚本：

- `scripts/build_stage0_band_gain_profiles.py`

## 原型边界

这不是最终 DSP 参数表。

它的定位是：

1. 给最小规则前置器原型一个明确的 band-gain 动作格式。
2. 先把 `brightness_up / brightness_down` 落成可消费的频带映射。
3. 先保证“方向正确、动作保守、频带明确”，再进入听感验证。

## 当前频带模板

当前采用设计文档里建议的 6 粗频带：

- `0–300 Hz`
- `300–800 Hz`
- `800–1500 Hz`
- `1500–3000 Hz`
- `3000–5000 Hz`
- `5000–8000 Hz`

## 当前动作模板

### 1. `brightness_up + high_band`

当前 normalized weights：

- `[0.00, 0.00, 0.35, 0.80, 1.00, 0.55]`

解释：

- 不直接碰最低两带
- 主提升落在 `1.5–5 kHz`
- `5–8 kHz` 只保留中等跟随，避免过度 air 化

### 2. `brightness_down + low_band`

当前 normalized weights：

- `[-0.40, -0.70, -1.00, -0.45, -0.10, 0.00]`

解释：

- 主抑制落在 `0.3–1.5 kHz`
- `1.5–3 kHz` 只保留较弱跟随
- 高频基本不动

## 当前强度换算

band-gain 文件里已经把 `alpha_default / alpha_max` 折成每带建议增益：

- `gain_db_default`
- `gain_db_max`

当前只是原型量级，数值仍然偏保守：

- 高强度女性向高区提亮，峰值也只有约 `+0.42 dB`
- 中强度男性向低区压亮，主抑制峰值约 `-0.28 dB`

## 当前适合怎么用

当前最适合的用法是：

1. 用 `rule_candidate_v1.json` 负责选规则。
2. 用 `rule_candidate_band_gain_profiles_v1.json` 负责把规则转成 band-gain 动作。
3. 在最小前置器原型里先实现“按频带乘一个温和 gain mask”。

## 当前不该怎么用

当前还不适合：

- 直接当成最终工程参数表
- 不做听感验证就扩大到 `speech`
- 直接引入 `forte / pp`

## 下一步

当前最自然的下一步是：

1. 把 selector 与 band-gain profile 接到最小规则前置器原型。
2. 给 band-gain profile 补更清晰的频带命名和听感解释。
3. 在少量固定样本上做第一轮规则试听。
