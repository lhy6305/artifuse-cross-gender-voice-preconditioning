# Stage 0 运行环境基线 v1

## 当前解释器

- `python.exe`
- 版本：`3.10.11`

## 当前已验证的关键依赖版本

- `numpy==1.23.5`
- `librosa==0.9.1`
- `pyworld==0.3.2`
- `soundfile==0.12.1`
- `scipy==1.14.1`
- `matplotlib==3.9.2`
- `pandas==2.2.3`

对应锁定文件见仓库根目录：`requirements-stage0-analysis.txt`

## 当前最小可运行分析入口

- 输入：
  - `data/datasets/_meta/utterance_manifest_clean_speech_v1.csv`
  - `data/datasets/_meta/utterance_manifest_clean_singing_v1.csv`
  - `experiments/fixed_eval/v1_2/fixed_eval_review_final_v1_2.csv`
- 脚本：
  - `scripts/run_stage0_baseline_analysis.py`
  - `scripts/run_stage0_baseline_full.ps1`
- 输出目录：
  - `experiments/stage0_baseline/v1_pilot/`
  - `experiments/stage0_baseline/v1_full/`

## 推荐运行方式

先跑 pilot：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

.\python.exe .\scripts\run_stage0_baseline_analysis.py `
  --pilot `
  --output-dir experiments/stage0_baseline/v1_pilot
```

确认链路没问题后，再跑全量。推荐拆成 `speech -> singing -> finalize` 三步，便于并行度控制和断点续跑：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

.\python.exe .\scripts\run_stage0_baseline_analysis.py `
  --subset speech `
  --output-dir experiments/stage0_baseline/v1_full `
  --jobs 6 `
  --batch-size 64 `
  --progress-every 50

.\python.exe .\scripts\run_stage0_baseline_analysis.py `
  --subset singing `
  --output-dir experiments/stage0_baseline/v1_full `
  --jobs 6 `
  --batch-size 64 `
  --progress-every 50

.\python.exe .\scripts\run_stage0_baseline_analysis.py `
  --finalize-only `
  --output-dir experiments/stage0_baseline/v1_full
```

如需用 PowerShell 手动入口，优先用：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

.\scripts\run_stage0_baseline_full.ps1 -Step speech
.\scripts\run_stage0_baseline_full.ps1 -Step singing
.\scripts\run_stage0_baseline_full.ps1 -Step finalize
```

常用可选项：

- `-Jobs <N>`：控制并行 worker 数。
- `-BatchSize <N>`：控制断点写盘粒度。
- `-ProgressEvery <N>`：控制进度打印频率。
- `-Overwrite`：清空已有 enriched CSV 后重跑当前步骤。
- `-OutputDir <path>`：改写输出目录，便于 smoke test 或单独实验。
- `-Pilot`：复用同一包装入口跑 `pilot` 模式。
- 第二个子集如果补齐了另一侧缓存，脚本会顺手刷新汇总文件；`-Step finalize` 主要用于只重建汇总而不再提特征。

## 当前设计边界

- 这是阶段 0 的第一版基线入口，不是最终分析总线。
- 先固定输入、特征字段和输出结构，再逐步补统计检验、图表和更大范围缓存。
- 第一版仍以 5 个核心分析方向为主：
  - `log-f0`
  - `uv / voiced`
  - `band energy` 的替代轻量入口
  - `spectral centroid`
  - `spectral tilt` 的替代轻量入口

## 备注

- 当前 `stage0 baseline` 直接复用 `scripts/enrich_manifest_features.py` 的特征定义，避免字段漂移。
- `full` 特征提取现在支持按 `subset` 分步执行、按稳定 `record_id` 断点续跑，并持续打印进度与 ETA；`utt_id` 仅保留作人类可读短名。
- 若后面切换更正式的 band energy / tilt 实现，应升级版本号，不要原地改写 `v1` 产物。
