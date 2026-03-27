# Representation Layer Pivot v1

## 为什么现在转型

到当前阶段为止，`stage0` 轻量前置器已经得到足够清晰的负证据：

- `static EQ / resonance tilt / formant anchor v1 / formant anchor v2`：`null_result`
- `WORLD-guided STFT delta`：`reject`
- `envelope warp v5`：虽然可辨识，但更像整体音调/音色重心拉动，没有真正击中共鸣主体

因此当前瓶颈不再是“参数再调一点”，而是：

- 缺少稳定、可编辑、能把 `f0` 与 tract / resonance 分开的表示层

项目目标也因此从“VC 前置模块”升级为：

- 构建并验证一个可解释的人声表示，使其能稳定承载性别相关的声道/共鸣信息

## 新阶段核心问题

1. 哪种表示最稳定地承载声道/共鸣信息？
2. 哪种表示与 `f0` 的纠缠最少？
3. 哪种表示更适合后续编辑与重建？

## 第一轮候选表示

本轮先不做复杂深度表示，先比较三条可解释路线：

1. `world_mel`
   - WORLD `cheaptrick` 谱包络
   - 压到 mel bins 后做 voiced 平均

2. `lpc_mel`
   - LPC 包络频响
   - 压到 mel bins 后做 voiced 平均

3. `mfcc`
   - 低阶 cepstral envelope proxy
   - 仅作为表示比较，不直接等同于可编辑 tract 参数

## 第一版工具链

本轮新增：

- `scripts/run_representation_layer_probe.py`
- `scripts/run_representation_layer_probe.ps1`

输出目录示例：

- `experiments/representation_layer/v1_fixed_eval_pilot/`
- `experiments/representation_layer/v1_clean_speech_probe/`

核心产物：

- `representation_probe_rows.csv`
- `representation_probe_summary.csv`
- `README.md`

## 当前 probe 做什么

它不直接生成听审包，而是先回答“表示值不值得继续做”：

1. 每条样本提取：
   - `world_mel`
   - `lpc_mel`
   - `mfcc`
2. 计算每种表示的：
   - voiced frame 数
   - 帧间 continuity
   - 每个数据集内的男女均值分离度
   - 组内散度与组间分离比

## 入口命令

固定评测集 pilot：

```powershell
.\scripts\run_representation_layer_probe.ps1 -InputMode fixed_eval
```

clean speech probe：

```powershell
.\scripts\run_representation_layer_probe.ps1 -InputMode clean_speech -SamplesPerCell 32
```

## 当前推进策略

1. 先用 fixed eval 跑通 probe 链路
2. 再扩到 clean speech 子集
3. 基于 separation / continuity 结果，选 1-2 条表示进入真正的编辑与重建阶段

## 明确停止项

从现在开始，不再继续新增 `stage0` 轻量前置器同族变体。

后续若继续生成听审包，前提必须是：

- 某种表示层先被证明“稳定且值得编辑”
