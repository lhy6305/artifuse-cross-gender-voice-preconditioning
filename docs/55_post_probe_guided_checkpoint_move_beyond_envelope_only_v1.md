# 表示层主线断点：停止继续抠 Envelope-Only 原始相位重建家族

## 断点目的

这份断点用于防止后续推进时，又重新回到：

- `probe-guided envelope v2 / v3`
- 继续拧 `keep_coeffs / probe_opt_steps / blend / max_frame_delta_l2`
- 在同一套“只改低阶包络、保留原始相位”的 envelope-only 家族里继续小修小补

当前需要固定的是一个更高层判断：

**到目前为止，envelope-only 原始相位重建家族已经给出了连续负证据。**

## 当前阶段结论

截至当前断点：

- `conditional_envelope_transport v1`：`8/8 no audible`
- `conditional_envelope_transport v2`：`8/8 no audible`
- `low-rank envelope subspace v1`：`8/8 no audible`
- `neural envelope latent v1`：`8/8 no audible`
- `conditioned neural envelope v1`：`8/8 no audible`
- `probe-guided envelope v1`：`8/8 no audible`

因此当前不能再把问题理解成：

- `probe` 还不够强
- `probe_opt_steps` 再加一点就会出来
- `blend / max_envelope_gain_db / time_smooth_frames` 再拧一版就能跨过阈值

## 强约束

从现在开始，默认不再继续以下动作：

1. 不继续出常规 `probe-guided envelope v2 / v3`
2. 不再沿整个 envelope-only 原始相位重建家族继续抠局部参数
3. 不再把“只改低阶包络而不碰 source proxy”当成当前主线

## 下一步原则

下一步应满足至少一条：

1. 从 `envelope-only` 升级到**joint source-filter representation**
2. 编辑对象不再只含 tract / envelope，而要显式带入**voiced harmonic residual / excitation proxy**
3. 若继续保留原始相位重建，也应改成“联合 residual feature + discriminative objective”的层级，而不是继续停在纯包络空间

## 接班口令

> 不要继续抠 envelope-only 原始相位重建家族。到 `2026-03-28` 为止，reference、low-rank、static neural、conditioned predictor、probe-guided 都是 `8/8 no audible`，下一步该升级到 joint source-filter residual 了。
