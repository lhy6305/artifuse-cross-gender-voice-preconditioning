# Stage1 RVC Cascade Eval Pivot v1

## 结论先行

截至当前，阶段 0 已经把“前置器自己单独听起来有没有明显变化”这条路基本走完了。

综合结果是：

- 大多数轻量方法：无可感知差异
- `envelope warp`：有时可感知，但容易不自然
- `WORLD full resynthesis`：可感知，但主要是底噪和脏瞬态
- `WORLD-guided STFT delta`：干净，但再次无感

所以当前不再把：

- `前置器单独试听是否明显`

当成主 gate。

接下来恢复到最初设计稿里的正式主指标：

- `前置器 + RVC 串联后是否整体改善`

## 为什么现在应该转这个 gate

`initial_design.md` 一开始就明确写了：

- 最终评价以“前置模块 + RVC 串联后的整体改善”为准，而非前置模块单独试听

现在前面的多轮试听已经足够说明：

- 要求前置器自己单独就有强耳感，未必是对的标准
- 更合理的标准是：它是否让下游 RVC 更容易做对跨性别映射

## 当前新增

已经新增第一版串联评测桥：

- `experiments/stage1_rvc_eval/v1/rvc_target_registry_v1.json`
- `scripts/build_stage1_rvc_cascade_manifest.py`
- `scripts/run_stage1_rvc_cascade_batch.py`
- `scripts/run_stage1_rvc_cascade_batch.ps1`
- `scripts/build_stage1_rvc_cascade_review_queue.py`
- `scripts/open_stage1_rvc_cascade_review_gui.ps1`
- `scripts/open_stage1_rvc_cascade_review_gui.cmd`

当前默认输入：

- `tmp/stage0_speech_world_stft_delta_listening_pack/v1/listening_pack_summary.csv`

当前默认目标：

- 本地可检测到的 `fzjv2.pth`

当前默认输出：

- `tmp/stage1_rvc_cascade_eval/v1/`

## 这条桥负责什么

它负责把同一批固定样本拆成两路：

1. `raw`
2. `preconditioned`

然后把这两路统一喂给同一个 RVC target，并生成：

- 可断点续跑的 `manifest csv`
- 统一的输出目录
- 统一的执行摘要

## 启动命令

先建 manifest：

```powershell
.\python.exe .\scripts\build_stage1_rvc_cascade_manifest.py
```

再跑批量推理：

```powershell
.\scripts\run_stage1_rvc_cascade_batch.ps1
```

如果只做 smoke：

```powershell
.\scripts\run_stage1_rvc_cascade_batch.ps1 -MaxRows 1
```

批跑完成后，直接打开成对听审：

```powershell
.\scripts\open_stage1_rvc_cascade_review_gui.ps1
```

如果你在 `cmd.exe` 里：

```cmd
.\scripts\open_stage1_rvc_cascade_review_gui.cmd
```

## 下一步

当前下一步不再是新前置器听审，而是：

1. 跑出 `raw vs preconditioned` 的 RVC 串联结果
2. 建一版最小人工对比清单
3. 判断这些“单独听起来几乎无感”的前置器，是否在串联后真的有帮助
