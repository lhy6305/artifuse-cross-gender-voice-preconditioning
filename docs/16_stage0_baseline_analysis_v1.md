# Stage 0 Baseline Analysis v1

## 目标

把当前已经冻结的输入资产真正接到一个可复跑的阶段 0 分析入口上：

- `clean_speech_v1`
- `clean_singing_v1`
- `fixed_eval v1_2`

## 当前脚本

- `scripts/run_stage0_baseline_analysis.py`

## 当前输出结构

- `experiments/stage0_baseline/<run_name>/input_snapshot/`
- `experiments/stage0_baseline/<run_name>/clean_speech_enriched.csv`
- `experiments/stage0_baseline/<run_name>/clean_singing_enriched.csv`
- `experiments/stage0_baseline/<run_name>/analysis_overview.csv`
- `experiments/stage0_baseline/<run_name>/gender_feature_summary.csv`
- `experiments/stage0_baseline/<run_name>/f0_bucket_summary.csv`
- `experiments/stage0_baseline/<run_name>/README.md`

## v1 做了什么

- 固定输入快照，避免后续“同名 clean subset 被替换”后不可复现。
- 复用现有轻量特征提取逻辑：
  - `rms_dbfs`
  - `peak_dbfs`
  - `clipping_ratio`
  - `silence_ratio_40db`
  - `zcr_mean`
  - `spectral_centroid_hz_mean`
  - `f0_voiced_ratio`
  - `f0_median_hz`
  - `f0_p10_hz`
  - `f0_p90_hz`
- 输出按 `gender` 分组的特征均值差。
- 输出基于 `f0_median_hz` 四分位的分桶统计。
- 同时把固定评测集终稿状态快照写进总表。
- `full` 入口支持 `speech` / `singing` 分步提取。
- `full` 特征提取支持按稳定 `record_id` 断点续跑。
- `full` 特征提取支持并行 worker 与周期性进度打印。
- 新增 PowerShell 手动入口：`scripts/run_stage0_baseline_full.ps1`

## 当前取舍

- 先不给 `v1` 强行补复杂显著性检验。
- 先不引入正式热图产出，避免把图形依赖和版式问题过早固定。
- `spectral tilt` 目前用 `log(spectral_centroid) - log(f0_median)` 的轻量近似入口占位；后续若切成正式实现，应单独升级版本号。

## 推荐推进顺序

1. 先跑 `pilot`，验证链路和字段。
2. 再跑 `full` 的 `speech` 子集，确认大规模缓存路径与进度输出稳定。
3. 跑 `full` 的 `singing` 子集。
4. 在两个 enriched CSV 都齐备后执行 `finalize-only`，生成阶段 0 第一版完整分析缓存。
5. 基于 `gender_feature_summary.csv` 和 `f0_bucket_summary.csv` 补图表与 markdown 报告。
6. 再决定是否扩展到更大的 `utterance_manifest` 子集。

## 推荐命令

### 直接调用 Python

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

### 使用 PowerShell 手动入口

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

.\scripts\run_stage0_baseline_full.ps1 -Step speech
.\scripts\run_stage0_baseline_full.ps1 -Step singing
.\scripts\run_stage0_baseline_full.ps1 -Step finalize
```

## 当前注意点

- `resume` 依赖稳定 `record_id`；`utt_id` 只保留作人类可读短名，不再承担全局唯一职责。
- 如果切换到新的输出目录，可避免 `pilot`、`smoke test` 和 `full` 之间互相污染缓存。
- 如需从头重跑某个子集，直接对该步骤使用 `--overwrite` 或 PowerShell 包装入口的 `-Overwrite`。
- 如果另一侧 enriched CSV 已存在，运行第二个子集时会自动刷新总表；`finalize-only` 主要用于只重建汇总文件。
