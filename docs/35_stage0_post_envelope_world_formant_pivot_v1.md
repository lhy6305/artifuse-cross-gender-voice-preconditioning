# Stage0 Post-Envelope/World Formant Pivot v1

## 为什么现在切回 formant-aware

最新一轮听审已经把两条并行线的边界说清楚了：

- `envelope warp v5`：方向已纠正，且几乎没有明显伪影，但听感更像整体音调/音色重心被拉动，不像真正命中共鸣主体
- `WORLD-guided STFT delta v4`：继续加力后伪影明显抬升，但性别改变幅度仍不够

因此下一步不再继续扩这两条线，而是回到更接近目标机理的：

- `voiced explicit formant-structure morph`

## 当前原型

本轮新增：

- `experiments/stage0_baseline/v1_full/speech_formant_anchor_candidate_v2.json`
- `artifacts/listening_review/stage0_speech_formant_listening_pack/v2/`

对应脚本与入口：

- `scripts/build_stage0_speech_formant_listening_pack.py`
- `scripts/open_stage0_speech_formant_review_gui.ps1`
- `scripts/open_stage0_speech_formant_review_gui.cmd`

## 这版和旧 formant v1 的区别

`v2` 不再是保守的双锚点轻推，而是：

1. 改成三锚点：`F1 / F2 / F3` 代理峰
2. 使用更窄的作用宽度
3. 提高 `boost / cut / shift_ratio`
4. 继续保留原始相位和 STFT 细节，不做整体 pitch 级拉伸

目标不是“更亮/更闷”，而是更明确地搬动共鸣结构。

## 当前量化快照

`v2` 的量化摘要位于：

- `artifacts/listening_review/stage0_speech_formant_listening_pack/v2/listening_review_quant_summary.md`

当前机器侧只说明：

- 比旧 `formant v1` 更强
- 但还没有强到可以跳过人工听审

## 启动命令

PowerShell:

```powershell
.\scripts\open_stage0_speech_formant_review_gui.ps1 -PackVersion v2
```

cmd.exe:

```cmd
.\scripts\open_stage0_speech_formant_review_gui.cmd -PackVersion v2
```
