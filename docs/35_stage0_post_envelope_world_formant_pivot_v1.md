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

## formant v2 人工听审结果

当前 `artifacts/listening_review/stage0_speech_formant_listening_pack/v2/` 已完成一轮人工听审。

人工结论非常明确：

- `8/8 effect_audible = no`
- 未出现值得记录的伪影问题

这意味着：

- 即使把 formant-aware 原型从保守双锚点升级到更强的三锚点局部搬移
- 在当前实现下，它仍然没有跨过稳定可感知阈值

## 阶段判断

到这一轮为止，可以把主线判断进一步收紧为：

1. `WORLD-guided STFT delta`：`reject`
2. `envelope warp`：`watch_with_risk`
   风险点不是伪影，而是更像整体音调/音色重心拉动，未击中核心共鸣目标
3. `formant-aware anchor morph v2`：`null_result`

因此当前不建议继续在 `stage0` 轻量前置器上新增同族变体。

更合理的下一步是：

- 把 `envelope v5` 仅作为“可辨识上限参考”
- 停止继续扩 `formant / world / resonance / static EQ`
- 转向：
  - `安全归一化 + 下游模型承担主变换`
  - 或更高层级的方法级 pivot，而不是继续做局部频谱小修正

## 启动命令

PowerShell:

```powershell
.\scripts\open_stage0_speech_formant_review_gui.ps1 -PackVersion v2
```

cmd.exe:

```cmd
.\scripts\open_stage0_speech_formant_review_gui.cmd -PackVersion v2
```
