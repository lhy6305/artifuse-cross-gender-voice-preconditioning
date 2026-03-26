# Stage0 Rule Review Quant GUI v1

## 新增入口

- `scripts/build_stage0_rule_review_queue.py`
- `scripts/stage0_rule_review_gui.py`
- `scripts/open_stage0_rule_review_gui.ps1`
- `scripts/open_stage0_speech_review_gui.ps1`
- `scripts/open_stage0_speech_review_gui.cmd`

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

新增的 speech-first 临时目录位于：

- `tmp/stage0_speech_listening_pack/v1/`

## 启动行为

`open_stage0_rule_review_gui.ps1` 当前改为：

- 默认直接打开已有 `listening_review_queue.csv`
- 仅在队列表不存在时自动重建
- 如需强制重建，使用 `-Rebuild`
- 可用 `-PackVersion v2` 之类的参数切到不同试听包目录

这样常规复审时不必每次等待量化预处理。

## 当前人工听审口径

当前这版 GUI 已改成：

- 默认按 `修正前 / 修正后` 做主观对照
- 如果读入的是 `stage1 cascade` 队列，也先忽略 `RVC` 输出
- 主判断回到：方向对不对、能不能听出、有没有伪影、强度是否合适、是否保留

## 当前交互布局

当前 GUI 已调整为：

- 左右双栏
- 左侧为文件列表，可拖动分隔条调整宽度
- 右侧详情区带纵向滚动条，避免长页面向下溢出
- 已移除 `审核人` 输入框
- 已去掉 `上一条 / 下一条 / 下一条未审` 按钮，改用左侧列表和键盘上下键切换
- 音量滑块长度已收缩，不再横向占满整行

## GUI Smoke

当前两个 Tk GUI 都已补 `--auto-close-ms`：

- `scripts/stage0_rule_review_gui.py`
- `scripts/fixed_eval_review_gui.py`

可用于最小联通性 smoke，而不必手动关窗。

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
- `review_notes`

## 当前实测结论

在当前 `v1` 试听包上，量化结果给出的结论是：

- 当前 band-gain 原型总体很保守，保真代价低
- 但代理指标推动普遍偏弱
- 第一轮自动评分更像“安全但不够到位”，而不是“已经形成稳定有效规则”

这正是 GUI 听审接下来要验证的点：

- 是否只是量化代理太严格，但听感其实已经成立
- 还是当前 gain 模板确实太弱，需要加大强度或改作用方式

## v2 强化试听包

当前已额外生成一版更激进的 `v2` profile：

- `experiments/stage0_baseline/v1_full/rule_candidate_band_gain_profiles_v2.json`
- `tmp/stage0_rule_listening_pack/v2/`

这版不是改规则选择逻辑，而是把 band-gain 强度整体放大到 `5x`：

- 高区 `brightness_up` 主带约到 `+1.5 dB`
- 低区 `brightness_down` 主带约到 `-0.9 dB`
- 弱规则也提升到约 `-0.6 dB`

当前 `v2` 的量化结论是：

- 相比 `v1`，`auto_quant_score` 均值从约 `34.09` 提到约 `44.23`
- `auto_effect_score` 均值从约 `10.12` 提到约 `27.30`
- 但整体仍未进入自动“通过”区

这说明：

- `v1` 确实太弱
- 但即使拉到 `v2`，当前静态 6 段 band-gain 也仍然偏保守
- 是否能听出来，需要继续靠 `v2` 人工听审确认

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

### 4. 强制重建后再打开

```powershell
.\scripts\open_stage0_rule_review_gui.ps1 -Rebuild
```

### 5. 打开 `v2` 试听包

```powershell
.\scripts\open_stage0_rule_review_gui.ps1 -PackVersion v2
```

### 6. GUI 自动退出 smoke

```powershell
.\python.exe .\scripts\stage0_rule_review_gui.py `
  --csv tmp/stage0_rule_listening_pack/v2/listening_review_queue.csv `
  --auto-close-ms 2000
```

也可以直接对 PowerShell 入口做 smoke：

```powershell
.\scripts\open_stage0_rule_review_gui.ps1 -PackVersion v2 -AutoCloseMs 2000
```

### 7. 打开 speech-first 听审包

```powershell
.\scripts\open_stage0_speech_review_gui.ps1
```

### 8. 在 `cmd.exe` 中打开 speech-first 听审包

```cmd
.\scripts\open_stage0_speech_review_gui.cmd
```
