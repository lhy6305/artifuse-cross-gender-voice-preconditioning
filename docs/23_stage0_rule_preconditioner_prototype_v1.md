# Stage 0 Rule Preconditioner Prototype v1

## 当前脚本

- `scripts/apply_stage0_rule_preconditioner.py`
- `scripts/build_stage0_rule_listening_pack.py`

## 作用

当前原型已经把这条链路接通：

1. `rule_candidate_v1.json` 负责按 `domain / style / f0 / target_direction` 选规则。
2. `rule_candidate_band_gain_profiles_v1.json` 负责把规则转成 band-gain 动作。
3. `apply_stage0_rule_preconditioner.py` 负责对单文件或小批量音频真正施加 band-gain。
4. `build_stage0_rule_listening_pack.py` 负责自动挑样本并导出试听包。

## 当前边界

这是 `prototype-only` 原型，不是最终前置器。

当前边界是：

- 仅面向 `singing`
- 仅覆盖当前候选规则启用的 style
- 只做静态 band-gain
- 不做 voiced mask
- 不做 envelope warp
- 不做更细的时变控制

## 当前试听包输出

试听包当前输出到临时目录：

- `tmp/stage0_rule_listening_pack/v1/`

其中包含：

- `original/`
- `processed/`
- `listening_pack_summary.csv`

当前 pack 共 `10` 条规则样本，一条规则对应一条样本。

## 当前验证状态

当前已经确认：

- selector 可以正确选中规则
- `forte / pp` 仍保持排除
- `processed` 音频与 `original` 音频存在实际波形差异，不是空操作

## 推荐用法

### 单文件

```powershell
.\python.exe .\scripts\apply_stage0_rule_preconditioner.py `
  --input-audio path\to\input.wav `
  --output-audio path\to\output.wav `
  --domain singing `
  --group-value slow_forte `
  --target-direction feminine `
  --f0-median-hz 410
```

### 自动试听包

```powershell
.\python.exe .\scripts\build_stage0_rule_listening_pack.py `
  --output-dir tmp/stage0_rule_listening_pack/v1
```

## 下一步

当前最自然的下一步是：

1. 对 `tmp/stage0_rule_listening_pack/v1/` 做第一轮人工试听。
2. 记录哪些 rule 方向正确但太弱，哪些已经可感知。
3. 再决定是否补 voiced mask 或 envelope warp。
