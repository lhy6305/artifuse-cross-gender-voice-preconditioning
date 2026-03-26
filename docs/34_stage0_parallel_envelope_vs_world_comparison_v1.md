# Stage0 Envelope Warp vs WORLD-STFT Parallel Comparison v1

## 目标

当前不再试图立刻决出唯一主线，而是让两条仍有残余证据的路线并行向前各走一步：

- `voiced-envelope-warp`
- `WORLD-guided voiced STFT delta`

比较的不是抽象偏好，而是两件事：

1. 改变量是否更稳定进入可辨识区
2. 输出质量是否仍保持可接受

## 当前已知状态

### 1. Envelope Warp

- `v1`：进入 `watch`
- `v2`：进入 `watch_with_risk`

当前判断：

- 它已经证明“这条作用方式可以出耳感”
- 但 `v2` 说明继续沿原方向硬推，很容易把质量一起拖坏

所以并行比较时不再沿 `v2` 继续加码，而是改成：

- `v3 = v1` 与 `v2` 之间的中间安全档

### 2. WORLD-guided STFT delta

- `v1`：复听后从 `null_result` 上调为 `watch`

当前判断：

- 它的优势是相对更干净
- 它的问题是可辨识样本仍偏少，且多为 `too_weak`

所以下一步自然是：

- `v2 = 小幅增强 + 更强平滑`

## 并行比较清单

### 统一约束

- 两线使用同一批固定样本
- 两线继续使用同一 GUI 和同一主观字段
- 仍按稀疏标注规则记录，不要求机械补满全部字段
- 每条线本轮只出一个新版本，不扩成版本树

### 本轮要做的包

1. `stage0_speech_envelope_listening_pack/v3`
2. `stage0_speech_world_stft_delta_listening_pack/v2`

### 听审重点

1. `effect_audible`
2. `direction_correct`
3. `artifact_issue`
4. `strength_fit`
5. `keep_recommendation`

### 通过标准

某条线若想保留到下一轮，至少应满足：

- `audible_yes + audible_maybe` 明显高于本线上一版
- 不出现批量 `artifact_issue = slight/yes`
- 不出现明显更多的 `direction_correct = no`

### 停线条件

某条线若出现以下任一情况，应停止：

- 仍只有零星 `audible_yes`
- 一增强就稳定出现 `artifact_issue`
- `keep_recommendation` 仍没有形成正向样本

## 当前建议

- `envelope warp`：看它能否在不重复 `v2` 风险的前提下保住耳感
- `WORLD-guided STFT delta`：看它能否在保持干净的前提下，把“少量可辨识”推成“稳定可辨识”

## 第二轮补充

上一轮 `envelope v3 / world v2` 的主观反馈已经收敛到同一个问题：

- 变化仍偏弱
- 很难稳定区分“整体音色轻微偏移”与“真正伪影/失真”

因此下一轮改为 `audibility stress test`：

- 目标优先级改成“先稳定听出差异”
- 不再把轻微整体音色偏移直接视为失败
- 只有当出现明确噪声、振铃、破碎感、瞬态脏化时，才记为 `artifact_issue`

本轮新增包：

1. `stage0_speech_envelope_listening_pack/v4`
2. `stage0_speech_world_stft_delta_listening_pack/v3`

## 第三轮补充

`v4 / v3` 听审后已出现两个新的明确判断：

- `envelope warp v4` 已能稳定听出，但主观方向整体反了：
  - `male -> feminine` 实际更 `male`
  - `female -> masculine` 实际更 `female`
- `WORLD-guided STFT delta v3` 主观方向正确，但整体仍然偏弱，远未到“足够”的程度

因此下一轮不再沿同一方式盲目加力，而是拆成：

1. `envelope v5 = 方向纠偏 + 保留 stress 强度`
2. `world v4 = 在主观方向正确前提下继续放大`

额外说明：

- 当前自动量化里的 `direction` 指标对这两条线都不再可直接信任
- `envelope` 由主观听审确认存在方向定义反转
- `world` 则出现“主观方向正确，但自动指标仍报 wrong_direction”的冲突
- 因此当前阶段以主观听审为主，量化只做改变量强弱参考

## 入口建议

Envelope Warp `v3`：

```powershell
.\scripts\open_stage0_speech_envelope_review_gui.ps1 -PackVersion v3
```

WORLD-guided STFT delta `v2`：

```powershell
.\scripts\open_stage0_speech_world_stft_delta_review_gui.ps1 -PackVersion v2
```

Envelope Warp `v4`：

```powershell
.\scripts\open_stage0_speech_envelope_review_gui.ps1 -PackVersion v4
```

WORLD-guided STFT delta `v3`：

```powershell
.\scripts\open_stage0_speech_world_stft_delta_review_gui.ps1 -PackVersion v3
```

Envelope Warp `v5`：

```powershell
.\scripts\open_stage0_speech_envelope_review_gui.ps1 -PackVersion v5
```

WORLD-guided STFT delta `v4`：

```powershell
.\scripts\open_stage0_speech_world_stft_delta_review_gui.ps1 -PackVersion v4
```
