# fixed_eval v1.2 final maybe resolution

## 决策

- 保留两条仅有轻微瞬态电平扰动、但仍具代表性的样本。
- 移除四条技巧性 singing 样本：三条 `lip_trill`，一条 `vocal_fry`。
- 只对新增替换进来的 4 条样本做补充听审，不需要再回听全部 96 条。

## 保留的原 maybe 样本

- `f2_arpeggios_f_slow_piano_a` | minor transient level jump only; still representative and otherwise clean
- `p230_107_mic1` | minor transient level jump only; speech content and bucket remain usable

## 移除样本

- `f1_arpeggios_lip_trill_a` | `singing_female` | lip_trill dominates the timbre; not representative of neutral singing input
- `f3_scales_lip_trill_o` | `singing_female` | lip_trill dominates the timbre; not representative of neutral singing input
- `m10_scales_vocal_fry_a` | `singing_male` | vocal_fry dominates the timbre; not representative of neutral singing input
- `m1_scales_lip_trill_o` | `singing_male` | lip_trill dominates the timbre; not representative of neutral singing input

## 替换关系

- `m1_scales_lip_trill_o` -> `m1_long_pp_a` | `singing_male` | `VocalSet 1.2` | `7-10s`
- `m10_scales_vocal_fry_a` -> `m10_scales_belt_i` | `singing_male` | `VocalSet 1.2` | `5-7s`
- `f1_arpeggios_lip_trill_a` -> `f1_arpeggios_breathy_u` | `singing_female` | `VocalSet 1.2` | `5-7s`
- `f3_scales_lip_trill_o` -> `f2_arpeggios_belt_u` | `singing_female` | `VocalSet 1.2` | `5-7s`
