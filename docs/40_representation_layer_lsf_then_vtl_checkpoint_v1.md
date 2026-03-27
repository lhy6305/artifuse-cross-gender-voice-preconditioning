# 表示层主线断点：先 LSF，后 VTL Warping

## 断点目的

这是一份显式接班断点，目的是防止后续自动推进时：

- 重新掉回 `LPC pole edit` 或 `cepstral delta` 的局部调参；
- 只盯单个实现细节，忽略当前主线已经收缩到更高层表示的问题。

## 当前阶段结论

截至当前断点：

- `LPC pole edit`：已主观确认是“可辨识但错误”的路线，阶段性 `reject`
- `cepstral envelope delta v1`：已主观确认“偏弱、方向可疑、像伪影/假高频”，最多保留为 `watch_with_risk`

因此：

**当前不再继续沿上述两类实现硬推。**

## 强约束的下一步顺序

下一阶段按以下固定顺序推进：

1. **先做 `LSF` 参数化原型**
   - 目标：验证 `LSF` 是否比直接 `pole edit` 更稳定、更少出现“小瓶子音 / 人造高频感”
   - 这是当前默认主线

2. **只有在 `LSF` 仍然不能给出正证据时，才进入 `VTL / tract-length warping`**
   - `VTL warping` 当前是明确的第二顺位候选
   - 不是与 `LSF` 并行铺开

3. **在 `LSF` 和 `VTL` 都没有形成正证据之前，不进入新的泛化黑盒路线**
   - 不直接跳到 latent 全局方向向量
   - 不直接跳到冻结后端训练小前置器

## 当前默认实现策略

- 先验证 `LSF` 是否能改善：
  - `female -> male` 的“瓶中感”
  - `male -> female` 的“刻意加高频感”
- 若仍失败，再把主线切到更物理一致的 `VTL warping`

## 接班提醒

下次推进时，若出现以下倾向，应视为偏离主线：

- 继续改 `LPC pole edit` 的局部 shift ratio
- 继续堆 `cepstral delta` 的强度版本
- 重新回到 `EQ / tilt / anchor / delta` 家族

## 当前接班口令

> 先试 `LSF`，如果不行，再试 `VTL warping`。不要回头在 `pole edit / cepstral delta` 上继续抠细节。
