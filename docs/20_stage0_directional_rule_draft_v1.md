# Stage 0 方向性规则草案 v1

## 这份草案的定位

这不是最终 DSP 参数表，也不是可以直接送进训练链路的强规则。

它的定位更保守：

1. 先把当前 `stage0 full` 能支持的方向性判断写清楚。
2. 先回答“往哪边修”而不是“具体修多少 dB / 哪条频带曲线”。
3. 给下一轮真正写规则表或前置器时提供一个收敛起点。

当前对应的结构化草案位于：

- `experiments/stage0_baseline/v1_full/directional_rule_draft_v1.csv`

## 一、总原则

### 1. `speech` 先不写统一亮度规则

虽然 `speech` 侧 `spectral_centroid_hz_mean` 在两个数据集上都表现为女高于男，但：

- `LibriTTS-R` 的 `mean_log_centroid_minus_log_f0` 在低/高区为正，中区为负
- `VCTK Corpus 0.92` 在两个可比较 bin 里都为负

这说明当前 `speech` 侧更适合：

- 保留为观察信号
- 用于筛规则
- 暂不直接写入第一版统一先验

### 2. `singing` 可以先按 style 和高低音区写方向

`singing` 侧比 `speech` 更适合先写方向性规则，因为：

- 多个 style 的高区都有稳定正向信号
- 一些 style 的低区也有稳定反向信号
- 自适应稳健分桶后，大多数 style 已经具备 `2` 个可比较 bin

### 3. 第一版只写“方向 + 强弱级别”

当前建议的强度标签只用：

- `weak`
- `medium`
- `medium_high`
- `high`

这一步故意不落成绝对增益，是为了避免把当前统计量过早误写成工程参数。

## 二、当前可激活的 singing 候选规则

### 1. 女性向高区提亮候选

这是当前最稳定的一条主线。

建议优先保留：

- `fast_forte high_band`：`medium_high`
- `slow_forte high_band`：`high`
- `straight high_band`：`high`
- `vibrato high_band`：`high`
- `slow_piano high_band`：`medium`
- `fast_piano high_band`：`medium`

共同含义：

- 如果目标方向更偏 feminine，可在对应 style 的高区启用保守提亮候选。

### 2. 男性向低区压亮候选

这条线没有高区那么统一，但在部分 style 上已经足够清晰：

- `straight low_band`：`medium`
- `vibrato low_band`：`medium`
- `slow_forte low_band`：`weak`
- `slow_piano low_band`：`weak`

共同含义：

- 如果目标方向更偏 masculine，可在低区做保守压亮候选。
- 这类规则应弱于女性向高区提亮候选。

### 3. 两端都正向的 style

`fast_forte` 和 `fast_piano` 当前在低区和高区都为正：

- 更接近“整体更亮”的 style
- 第一版可以先只保留方向，不做低区额外压暗

## 三、当前不进入常规规则表的项

### 1. `speech`

当前不建议把 `speech` 侧直接写成统一规则，原因是：

- 跨数据集条件不稳定
- 条件桶方向还不够一致
- 更适合先继续作为描述性观察和筛选信号

### 2. `forte` / `pp`

这两个 style 当前只在中间窄重叠区存在可比较样本。

因此：

- 暂不纳入第一版常规规则表
- 只保留“中间可比较区偏 male-higher”的备注

## 四、建议的第一版执行边界

如果下一步要把这份草案真正写进一个保守版前置器，我建议边界如下：

1. 只在 `singing` 域启用。
2. 只对 `fast_forte`、`fast_piano`、`slow_forte`、`slow_piano`、`straight`、`vibrato` 启用。
3. 女性向只先开高区候选。
4. 男性向只先开 `straight / vibrato` 的低区候选，再视情况补 `slow_*`。
5. `speech`、`forte`、`pp` 继续留在观察态，不作为 v1 常规启用项。

## 五、建议的下一步

下一步最自然的是：

1. 把 `directional_rule_draft_v1.csv` 再收缩成真正的 v1 候选规则表。
2. 为每条规则补一个保守强度上限区间。
3. 准备后续和前置器设计对接时用的最小配置格式。

## 最后一句

当前最重要的不是把规则写满，而是：

- 先只启用最稳定、最可解释、最不容易过修正的那几条；
- 让第一版规则草案先具备“方向正确、强度保守、边界明确”这三个条件。
