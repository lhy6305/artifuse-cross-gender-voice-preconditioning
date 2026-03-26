# Stage0 Resonance Tilt 听审反馈与 Formant Anchor Pivot v1

## resonance tilt 听审结论

`speech resonance tilt v1` 的人工结论也已经很清楚：

- 没有任何样本出现可感知差异
- 但也没有出现失真或不自然感

这意味着：

- `resonance tilt` 比 `envelope warp` 更安全
- 但它仍然太弱
- 问题不再是“自然不自然”，而是“没有真正打到可感知的 formant / resonance 主体”

## 为什么改成 formant anchor morph

下一步改成：

- `voiced adaptive formant-anchor morph`

核心思路：

1. 仍然只在 voiced 段处理
2. 先从平滑谱包络里找每帧的 `F1 / F2` 代理峰
3. 围绕这些峰做宽带 boost / cut 对
4. 用“上移 / 下移 anchor”的方式做更强、但仍然局部的共鸣搬移

相比前两条路线：

- 比 `envelope warp` 更局部，不会把整条包络拉窄
- 比 `resonance tilt` 更有针对性，不只是全局宽带轻推

## 当前原型

已经新增：

- `experiments/stage0_baseline/v1_full/speech_formant_anchor_candidate_v1.json`
- `scripts/build_stage0_speech_formant_listening_pack.py`
- `scripts/open_stage0_speech_formant_review_gui.ps1`
- `scripts/open_stage0_speech_formant_review_gui.cmd`

临时目录：

- `tmp/stage0_speech_formant_listening_pack/v1/`

当前这版原型已经实际生成了试听包和量化队列表。

## 当前量化快照

当前 `8` 条 speech 样本的量化摘要：

- `avg auto_quant_score = 37.42`
- `avg auto_direction_score = 8.57`
- `avg auto_preservation_score = 100.00`
- `avg auto_effect_score = 14.26`
- `8/8 fail`

这说明机器侧已经在提示：

- 当前 formant anchor `v1` 比 resonance tilt 还弱
- 它目前更像探索性分支，而不是已经胜出的主线

## formant anchor 人工听审结果

当前 `tmp/stage0_speech_formant_listening_pack/v1/` 已完成一轮人工听审。

人工结论：

- `8/8 effect_audible = no`
- 没有出现失真
- 也没有出现明显不自然感

这意味着：

- 这条路线仍然是“安全但无感”
- 到这里为止，`static EQ / envelope warp / resonance tilt / formant anchor` 四条轻量频谱前置路线都没有在人耳上形成稳定成立的结果

## 当前阶段判断

现在更合理的动作不是继续在同一范式里堆更多小变体，而是做阶段门判断：

- `lightweight spectral preconditioning` 作为“人耳可感知的独立前置修正”路线，得到阶段性 `null result`

## 后续方向

后续如果还要继续，应优先考虑：

1. 更强的 source-filter / vocal-tract 级方法
2. 把前置器角色收缩为“安全归一化”，不再追求人耳独立可辨
3. 把真正的性别共鸣迁移交给更强的下游模型或 formant-aware 路线

## 启动命令

PowerShell:

```powershell
.\scripts\open_stage0_speech_formant_review_gui.ps1
```

`cmd.exe`:

```cmd
.\scripts\open_stage0_speech_formant_review_gui.cmd
```
