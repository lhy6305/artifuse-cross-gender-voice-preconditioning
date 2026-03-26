# Stage0 静态 EQ Null Result 与 Envelope Warp Pivot v1

## 当前阶段性结论

到目前为止，已经完成三轮人工听审：

- `singing` 静态 6 段 EQ `v1`
- `singing` 静态 6 段 EQ `v2`
- `speech-first` 静态 6 段 EQ `v1`

人工结论一致：

- 全部样本均无可感知差异

`speech-first` 队列表中的人工字段也已经写回：

- `8/8 reviewed`
- `8/8 effect_audible = no`
- `8/8 strength_fit = too_weak`

这意味着当前可以正式下一个阶段判断：

- 不再继续微调静态 6 段 EQ
- 当前静态 EQ 路线在人耳上已经可以视为 `null result`

## 为什么现在应该换作用方式

静态 6 段 EQ 的问题已经不是“代码没生效”，而是：

1. 量化上能看到变化
2. 人耳上连续三轮都听不出来
3. 继续只调 gain 大小，信息增益很低

换句话说，问题不再是“推得不够多一点点”，而是“这种作用方式本身太钝”。

## 下一条路线

下一步改成：

- `voiced-envelope-warp`

核心思路：

1. 先估计每帧的平滑谱包络
2. 只在 voiced 段上处理
3. 直接把谱包络沿频率轴做轻度上移或下移
4. 再把这个包络变化乘回原始谱上

相比静态 6 段 EQ，这种方法更像：

- 改共鸣壳体走势

而不是：

- 粗暴给几个固定频段加减一点点电平

## 为什么先做 voiced-only

如果直接全频全时段硬推，更容易把：

- 擦音
- 爆破音
- 辅音边界

一起改坏。

所以第一版 envelope warp 先限制在 voiced 段，优先看：

- 元音 / 共鸣主体能否终于产生可感知差异

## 已落下的原型

当前已经新增：

- `experiments/stage0_baseline/v1_full/speech_envelope_warp_candidate_v1.json`
- `scripts/build_stage0_speech_envelope_listening_pack.py`
- `scripts/open_stage0_speech_envelope_review_gui.ps1`
- `scripts/open_stage0_speech_envelope_review_gui.cmd`

临时产物目录约定为：

- `tmp/stage0_speech_envelope_listening_pack/v1/`

当前这版原型已经实际生成了试听包和量化队列表。

## 当前量化快照

在当前 `8` 条 speech 样本上，第一版 envelope warp 的量化摘要为：

- `avg auto_quant_score = 42.40`
- `avg auto_direction_score = 8.46`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score = 34.39`
- `8/8 auto_quant_grade = fail`

这说明：

- 它仍然保持了很高保真
- 也确实比“几乎空操作”更有改动
- 但当前代理指标还没有显示出稳定方向性

所以这一步更需要人工听审来回答：

- 虽然代理口径不漂亮，但人耳上是否终于开始可感知

## v1 人工听审结果

当前 `tmp/stage0_speech_envelope_listening_pack/v1/` 已完成一轮人工听审。

结果不是“全部无感”，而是：

- 已经出现部分可感知差异
- 但仅在部分样本上可感知
- 且整体差异仍然偏小

写回结果摘要：

- `2/8 effect_audible = yes`
- `6/8 effect_audible = maybe`
- `2/8 keep_recommendation = maybe`
- `2/8 direction_correct = maybe`
- `8/8 strength_fit = too_weak 或留空但整体偏弱`

更具体地说：

- 当前最明确开始“有耳感”的是 `LibriTTS-R / female -> masculine`
- 其余样本大多是“似乎有一点，但还不够确定”

这说明：

- `voiced-envelope-warp` 已经比静态 EQ 更接近可感知区间
- 但 `v1` 强度仍然偏弱
- 下一步不该换方法，而该先做定向补强的 `v2`

## v2 调整策略

当前已经基于这轮听审结果，生成：

- `experiments/stage0_baseline/v1_full/speech_envelope_warp_candidate_v2.json`
- `tmp/stage0_speech_envelope_listening_pack/v2/`

调整原则不是“全部粗暴拉大”，而是：

- `feminine` 侧加大更多，优先补强此前 mostly-maybe 的样本
- `LibriTTS-R masculine` 侧只做中等上调，避免把已开始可感知的样本一下推过头
- 同时降低 `envelope_smooth_bins`、提高 `voiced_rms_gate_db`，让 warp 更集中在真正有共鸣主体的区段

## v2 量化快照

当前 `v2` 的量化摘要已经生成：

- `avg auto_quant_score = 53.16`
- `avg auto_direction_score = 24.51`
- `avg auto_preservation_score = 96.54`
- `avg auto_effect_score = 52.69`
- `1 strong_pass + 1 borderline + 6 fail`

其中最强的是：

- `VCTK male -> feminine` 两条

这说明：

- `v2` 相比 `v1` 已明显更强
- 当前最值得优先再次人工确认的是 `VCTK male -> feminine`

## 第一版 envelope warp 参数

当前第一版不是正式规则，只是可感知性探针。

默认参数大致为：

- `LibriTTS-R masculine -> feminine`: `warp_factor = 1.12`
- `VCTK masculine -> feminine`: `warp_factor = 1.08`
- `LibriTTS-R feminine -> masculine`: `warp_factor = 0.90`
- `VCTK feminine -> masculine`: `warp_factor = 0.92`
- `blend = 0.85 ~ 0.90`
- `max_envelope_gain_db = 6 ~ 7 dB`

## 当前判断标准

如果这版 envelope warp 仍然：

- 人耳完全无感

那就基本可以认为：

- “轻量可解释前置修正” 至少在当前静态/半静态频谱处理范式下，不足以构成有效听感变化

那时再考虑是否直接跳到：

- 更强的 formant-aware 路线
- 或者把前置修正退回“只做安全保真，不追求人耳独立可辨”

## 启动命令

PowerShell:

```powershell
.\scripts\open_stage0_speech_envelope_review_gui.ps1
```

`cmd.exe`:

```cmd
.\scripts\open_stage0_speech_envelope_review_gui.cmd
```

打开 `v2`：

```powershell
.\scripts\open_stage0_speech_envelope_review_gui.ps1 -PackVersion v2
```

```cmd
.\scripts\open_stage0_speech_envelope_review_gui.cmd -PackVersion v2
```
