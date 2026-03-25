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
- 输出目录：
  - `experiments/stage0_baseline/v1/`

## 推荐运行方式

先跑 pilot：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

.\python.exe .\scripts\run_stage0_baseline_analysis.py `
  --pilot `
  --output-dir experiments/stage0_baseline/v1_pilot
```

确认链路没问题后，再跑全量：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

.\python.exe .\scripts\run_stage0_baseline_analysis.py `
  --output-dir experiments/stage0_baseline/v1_full
```

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
- 若后面切换更正式的 band energy / tilt 实现，应升级版本号，不要原地改写 `v1` 产物。
