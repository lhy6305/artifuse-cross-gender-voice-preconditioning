# fixed_eval v1.1 review resolution

## 决策

- 移除所有已标记且确属特殊发声技巧的 singing 样本：`trillo`、`lip_trill`、`vocal_fry`、`inhaled`。
- 移除带明显咳嗽 / 清嗓尾音的 speech 样本。
- 移除两条听感性别指向不清的 speech 样本，保持固定评测桶的清晰度。
- 保留其余样本，尽量不打乱已经完成的人工听审结果。

## 已移除样本

- `m1_long_inhaled_u` | `singing_male` | `VocalSet 1.2` | special phonation: inhaled long tone; not a neutral singing benchmark
- `m11_scales_vocal_fry_i` | `singing_male` | `VocalSet 1.2` | special phonation: vocal fry; not a neutral singing benchmark
- `m4_long_trillo_e` | `singing_male` | `VocalSet 1.2` | special phonation: trillo; unstable / discontinuous singing texture
- `m1_scales_lip_trill_a` | `singing_male` | `VocalSet 1.2` | special phonation: lip trill; not a neutral singing benchmark
- `f1_scales_lip_trill_a` | `singing_female` | `VocalSet 1.2` | special phonation: lip trill; not a neutral singing benchmark
- `f5_arpeggios_lip_trill_o` | `singing_female` | `VocalSet 1.2` | special phonation: lip trill; not a neutral singing benchmark
- `f3_scales_lip_trill_u` | `singing_female` | `VocalSet 1.2` | special phonation: lip trill; not a neutral singing benchmark
- `f6_scales_vocal_fry_e` | `singing_female` | `VocalSet 1.2` | special phonation: vocal fry; not a neutral singing benchmark
- `p252_391_mic1` | `speech_male` | `VCTK Corpus 0.92` | speech sample contains end-of-utterance cough / throat-clearing artifact
- `1284_1180_000007_000001` | `speech_female` | `LibriTTS-R` | auditory gender salience unclear; exclude from fixed benchmark bucket
- `2078_142845_000085_000003` | `speech_male` | `LibriTTS-R` | auditory gender salience unclear; exclude from fixed benchmark bucket

## 替换关系

- `m1_long_inhaled_u` -> `m1_scales_belt_a` | `singing_male` | `VocalSet 1.2` | `5-7s`
- `m11_scales_vocal_fry_i` -> `m10_scales_belt_i` | `singing_male` | `VocalSet 1.2` | `5-7s`
- `m4_long_trillo_e` -> `m11_arpeggios_breathy_u` | `singing_male` | `VocalSet 1.2` | `5-7s`
- `m1_scales_lip_trill_a` -> `m1_long_pp_a` | `singing_male` | `VocalSet 1.2` | `7-10s`
- `p252_391_mic1` -> `p226_011_mic1` | `speech_male` | `VCTK Corpus 0.92` | `7-10s`
- `f1_scales_lip_trill_a` -> `f1_arpeggios_breathy_u` | `singing_female` | `VocalSet 1.2` | `5-7s`
- `f5_arpeggios_lip_trill_o` -> `f2_arpeggios_belt_a` | `singing_female` | `VocalSet 1.2` | `5-7s`
- `f3_scales_lip_trill_u` -> `f4_arpeggios_vibrato_e` | `singing_female` | `VocalSet 1.2` | `5-7s`
- `f6_scales_vocal_fry_e` -> `f5_arpeggios_belt_e` | `singing_female` | `VocalSet 1.2` | `5-7s`
- `1284_1180_000007_000001` -> `1284_1181_000047_000000` | `speech_female` | `LibriTTS-R` | `3-5s`
- `2078_142845_000085_000003` -> `1089_134686_000009_000003` | `speech_male` | `LibriTTS-R` | `5-7s`

## 保留的原存疑样本

- `f2_arpeggios_f_slow_piano_a` | keep for now; only slight issue noted and still representative
- `p230_107_mic1` | keep for now; sentence remains usable and bucket assignment is clear

## 后续建议

- 仅对新增替换进来的样本做补充听审，不需要全量重听。
- 如果后续还要进一步提纯 singing 基准集，可以考虑把 `VocalSet` 中更多技巧性标签整体排除出固定评测集。
