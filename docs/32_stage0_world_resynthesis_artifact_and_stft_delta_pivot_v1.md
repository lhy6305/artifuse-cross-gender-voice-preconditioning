# Stage0 WORLD Resynthesis Artifact And STFT Delta Pivot v1

## 听审结论

`WORLD source-filter / vocal-tract morph v1` 的人工听审已经完成。

结论不是“方向不够稳”，而是更基础的问题：

- 全部样本都出现明显底噪
- 能听到类似接线接触不良的瞬态干扰
- 人声本身几乎没有形成目标方向变化

所以这版不应继续调 `warp_ratio / blend`，因为当前主要失败点不是参数轻重，而是：

- `WORLD` 全量重合成链路本身把副作用先带进来了

## 机器侧为什么误判

这版机器侧分数很高，但人耳不认可，原因很直接：

- `auto_effect_score` 会把“噪声、脏瞬态、频谱扰动”也算成显著变化
- 但这些变化不等于“性别共鸣方向变化”

因此当前可以补一个更硬的判断：

- `WORLD full resynthesis` 这条实现方式，至少在当前参数和链路下，不适合作为阶段 0 的直接试听原型

## 新 pivot

下一步不再让 `WORLD` 负责整段重合成，而是改成：

- `WORLD analysis only`
- 从 `WORLD` 里提取谱包络差分
- 把这个差分只作用到原始波形的 `STFT magnitude`
- 保留原始相位和原始时域细节
- 只在 `voiced` 段启用

这条新路线可以概括为：

- `WORLD-guided voiced STFT delta`

目标是把“source-filter 层级的更强方向信息”保留住，同时避开：

- WORLD 重合成带来的底噪
- 瞬态脏声
- 原始细节被重建器抹掉

## 当前新增

已经新增：

- `experiments/stage0_baseline/v1_full/speech_world_stft_delta_candidate_v1.json`
- `scripts/build_stage0_speech_world_stft_delta_listening_pack.py`
- `scripts/open_stage0_speech_world_stft_delta_review_gui.ps1`
- `scripts/open_stage0_speech_world_stft_delta_review_gui.cmd`

临时目录：

- `tmp/stage0_speech_world_stft_delta_listening_pack/v1/`

## 启动命令

PowerShell:

```powershell
.\scripts\open_stage0_speech_world_stft_delta_review_gui.ps1
```

`cmd.exe`:

```cmd
.\scripts\open_stage0_speech_world_stft_delta_review_gui.cmd
```
