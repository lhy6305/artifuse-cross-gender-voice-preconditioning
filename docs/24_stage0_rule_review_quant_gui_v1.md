# Stage0 Rule Review Quant GUI v1

## 新增入口

- `scripts/build_stage0_rule_review_queue.py`
- `scripts/stage0_rule_review_gui.py`
- `scripts/open_stage0_rule_review_gui.ps1`

## 作用

当前这套补的是两件事：

1. 不再只凭耳朵判断，而是先对 `original / processed` 做一轮可复核的量化对比。
2. 把量化结果直接放进 GUI，边听边写回评审结论。

## 临时目录约定

当前默认输入和输出都放在：

- `tmp/stage0_rule_listening_pack/v1/`

这里的内容属于可重建临时产物：

- `original/`
- `processed/`
- `listening_pack_summary.csv`
- `listening_review_queue.csv`
- `listening_review_quant_summary.md`

如果你手动清空了 `tmp/`，应先重跑试听包构建，再重跑量化队列表生成。

## 当前量化口径

### 1. 主方向

主代理指标：

- `delta_log_centroid_minus_log_f0`

当前解释规则：

- `brightness_up / feminine` 期望该值为正
- `brightness_down / masculine` 期望该值为负
- `|delta| >= 0.015` 视为已有方向
- `|delta| >= 0.030` 视为更明显

### 2. 改变量

同时观察：

- `delta_spectral_centroid_hz_mean`
- `delta_low_mid_0_1500_share_db`
- `delta_brilliance_3000_8000_share_db`

其中：

- `high_band` 规则优先看高频占比是否上升
- `low_band` 规则优先看低中频占比是否下降

### 3. 保真代价

当前 GUI 里会直接展示这些差异：

- `delta_f0_median_pct`
- `delta_rms_dbfs`
- `delta_f0_voiced_ratio`
- `delta_clipping_ratio`
- `stft_logmag_l1`

当前建议线：

- `F0 drift <= 3%`
- `RMS drift <= 1.5 dB`
- `voiced ratio drift <= 0.08`
- `clipping increase` 尽量接近 `0`

## 自动评分字段

队列表当前会自动写出：

- `auto_direction_score`
- `auto_preservation_score`
- `auto_effect_score`
- `auto_quant_score`
- `auto_direction_flag`
- `auto_preservation_flag`
- `auto_audibility_flag`
- `auto_quant_grade`
- `auto_quant_notes`

它们不是最终结论，只是帮助你更快定位：

- 方向大体对不对
- 改动是否过弱
- 保真代价是否偏大

## GUI 人工字段

GUI 写回字段包括：

- `review_status`
- `direction_correct`
- `effect_audible`
- `artifact_issue`
- `strength_fit`
- `keep_recommendation`
- `reviewer`
- `review_notes`

## 当前实测结论

在当前 `v1` 试听包上，量化结果给出的结论是：

- 当前 band-gain 原型总体很保守，保真代价低
- 但代理指标推动普遍偏弱
- 第一轮自动评分更像“安全但不够到位”，而不是“已经形成稳定有效规则”

这正是 GUI 听审接下来要验证的点：

- 是否只是量化代理太严格，但听感其实已经成立
- 还是当前 gain 模板确实太弱，需要加大强度或改作用方式

## 推荐命令

### 1. 重建试听包

```powershell
.\python.exe .\scripts\build_stage0_rule_listening_pack.py `
  --output-dir tmp/stage0_rule_listening_pack/v1
```

### 2. 生成量化评审表

```powershell
.\python.exe .\scripts\build_stage0_rule_review_queue.py `
  --summary-csv tmp/stage0_rule_listening_pack/v1/listening_pack_summary.csv `
  --output-csv tmp/stage0_rule_listening_pack/v1/listening_review_queue.csv
```

### 3. 打开听审 GUI

```powershell
.\scripts\open_stage0_rule_review_gui.ps1
```
