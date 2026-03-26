# Stage0 Envelope Warp 听审反馈与 Resonance Tilt Pivot v1

## v2 听审结论

`speech envelope warp v2` 的人工结论已经很明确：

- `female -> masculine` 侧虽然更容易听见了
- 但听感更像频带被收窄
- 开始出现不自然感
- 并没有形成“更像 male resonance”的共鸣补强

而 `male -> feminine` 侧则是：

- 可感知变化仍然较小
- 或直接没有

这说明当前 `envelope warp` 的问题不是“再推一点就好”，而是：

- 它更容易把包络形状拉窄
- 而不是补出更自然的共鸣壳体

## 为什么改成 resonance tilt

下一步不再沿频率轴拉扯包络，而是改成：

- `voiced broad-resonance tilt`

核心原则：

1. 仍然只在 voiced 段处理
2. 不去平移/压缩谱包络
3. 只做连续、宽带、低 Q 的共鸣倾斜

目标：

- `masculine` 侧更像“补 600-1200 Hz 壳体 + 压一点 3k 刺点”
- `feminine` 侧更像“减一点胸腔闷感 + 补 presence / brilliance”

## 当前原型

已经新增：

- `experiments/stage0_baseline/v1_full/speech_resonance_tilt_candidate_v1.json`
- `scripts/build_stage0_speech_resonance_listening_pack.py`
- `scripts/open_stage0_speech_resonance_review_gui.ps1`
- `scripts/open_stage0_speech_resonance_review_gui.cmd`

临时目录：

- `tmp/stage0_speech_resonance_listening_pack/v1/`

当前这版原型已经实际生成了试听包和量化队列表。

## 当前量化快照

当前 `8` 条 speech 样本的量化摘要：

- `avg auto_quant_score = 52.75`
- `avg auto_direction_score = 32.07`
- `avg auto_preservation_score = 99.55`
- `avg auto_effect_score = 33.82`
- `borderline = 2`
- `fail = 6`

更具体地说：

- `LibriTTS-R male -> feminine` 两条已经到 `borderline`
- `LibriTTS-R female -> masculine` 两条方向也终于不再明显反向
- `VCTK` 两侧暂时仍偏弱

这说明当前 broad-resonance tilt 至少在机器口径上：

- 没有再重复 envelope warp 的“female 侧反而越推越假”的问题
- 但整体强度仍然偏保守
- 下一步需要靠人工听审确认：它是不是比 envelope warp 更自然

## 启动命令

PowerShell:

```powershell
.\scripts\open_stage0_speech_resonance_review_gui.ps1
```

`cmd.exe`:

```cmd
.\scripts\open_stage0_speech_resonance_review_gui.cmd
```
