# 任务与分支映射

## 当前状态
- 当前仓库还处于开题与整备阶段，没有必须绑定到真实 Git 分支的并行开发流。
- 本文档先记录任务切分和建议边界，等后续出现实际分支后再补充映射关系。

## 当前任务切分

| 任务 | 目标 | 当前状态 | 主要落点 |
|---|---|---|---|
| 仓库整备 | 固定文档入口、编码规范、Git 边界 | 已完成第二轮 | `docs/`、`.gitignore`、`.gitattributes`、`.editorconfig` |
| 实验记录骨架 | 固定日报、实验记录、关键 checkpoint 落位 | 已完成首轮 | `reports/daily/`、`experiments/`、`artifacts/checkpoints/keep/` |
| 环境冻结 | 固定 Python/Torch/音频处理环境 | 已完成首轮 | `docs/15_stage0_runtime_environment_v1.md`、`requirements-stage0-analysis.txt` |
| 第三方依赖边界 | 明确上游 RVC 代码是参考副本还是纳管依赖 | 待开始 | `third_party/` 或根目录参考位点 |
| 数据资产盘点 | 建立数据总表与评测集方案 | 已完成首轮 | `data/datasets/_meta/`、`docs/12_dataset_inventory_first_pass.md` |
| 固定评测集 v1 | 冻结第一版评测桶、配额、规则与清单 | 已完成首轮 | `docs/13_fixed_eval_sampling_v1.md`、`scripts/sample_fixed_eval_set.py`、`experiments/fixed_eval/v1/` |
| 人工巡检工具链 | 用最少操作完成 fixed eval 听审与记录 | 已完成首轮 | `scripts/open_fixed_eval_review_gui.ps1`、`scripts/fixed_eval_review_gui.py`、`experiments/fixed_eval/v1/review_pack/` |
| clean analysis subsets | 生成保守可复现的 speech / singing 主分析子集 | 已完成首轮 | `scripts/build_clean_analysis_subsets.py`、`data/datasets/_meta/utterance_manifest_clean_*.csv`、`docs/14_clean_analysis_subsets_v1.md` |
| 分析脚本落地 | 实现阶段 0/1 所需预处理与统计脚本 | 已完成首轮 | `scripts/run_stage0_baseline_analysis.py`、`docs/16_stage0_baseline_analysis_v1.md`、`experiments/stage0_baseline/` |
| 表示层升级主线 | 在已否定 `pole edit / cepstral delta`、低先验 `envelope-only` 家族与 `source-filter residual v1` 后，当前已切到 `machine-first` 探测阶段；`LSF v2` 已给出“全包可辨但偏弱”的首个连续主观正信号，当前已进一步推进到更强的 `LSF v3`，等待正式听审 | 进行中 | `docs/40_representation_layer_lsf_then_vtl_checkpoint_v1.md`、`docs/41_representation_layer_lsf_probe_v1.md`、`docs/42_representation_layer_vtl_warping_probe_v1.md`、`docs/43_representation_layer_vtl_warping_probe_v2.md`、`docs/44_post_lsf_vtl_checkpoint_move_beyond_classic_warping_v1.md`、`docs/45_representation_layer_conditional_envelope_transport_probe_v1.md`、`docs/46_representation_layer_conditional_envelope_transport_probe_v2.md`、`docs/47_post_conditional_transport_checkpoint_move_beyond_reference_envelope_v1.md`、`docs/48_representation_layer_low_rank_envelope_subspace_probe_v1.md`、`docs/49_post_low_rank_checkpoint_move_beyond_linear_subspace_v1.md`、`docs/50_representation_layer_neural_envelope_latent_probe_v1.md`、`docs/51_post_neural_checkpoint_move_beyond_static_latent_mapping_v1.md`、`docs/52_representation_layer_conditioned_neural_envelope_probe_v1.md`、`docs/53_post_conditioned_predictor_checkpoint_move_beyond_mapping_family_v1.md`、`docs/54_representation_layer_probe_guided_envelope_probe_v1.md`、`docs/55_post_probe_guided_checkpoint_move_beyond_envelope_only_v1.md`、`docs/56_representation_layer_source_filter_residual_probe_v1.md`、`docs/57_machine_first_review_gate_v1.md`、`docs/58_representation_layer_lsf_probe_v2.md`、`docs/59_representation_layer_lsf_probe_v3.md`、`scripts/build_listening_machine_gate_report.py`、`scripts/run_lsf_machine_sweep.py` |

## 当前显式断点
- 当前主线接班断点已固定在：`docs/40_representation_layer_lsf_then_vtl_checkpoint_v1.md`
- `LSF v1` 已进入可听审状态：
- `LSF v1` 已完成听审并给出负向结论：
  - 配置：`experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v1.json`
  - 入口：`scripts/open_stage0_speech_lsf_review_gui.ps1 -PackVersion v1`
  - 正式包：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v1/`
  - 主观结果：整体仍偏弱，且部分样本已出现伪影
- `VTL v1` 已进入可听审状态：
- `VTL v1` 已完成听审并暴露复杂失效模式：
  - 配置：`experiments/stage0_baseline/v1_full/speech_vtl_warping_candidate_v1.json`
  - 入口：`scripts/open_stage0_speech_vtl_review_gui.ps1 -PackVersion v1`
  - 正式包：`artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v1/`
  - 当前机器侧先验：`fail=8/8`
  - 主观结果：部分样本可辨，但备注显示局部低 `f0` 才生效、`F0` 对齐版本伪影重、部分样本有双声感
- `VTL v2` 已进入可听审状态：
  - 配置：`experiments/stage0_baseline/v1_full/speech_vtl_warping_candidate_v2.json`
  - 入口：`scripts/open_stage0_speech_vtl_review_gui.ps1 -PackVersion v2`
  - 正式包：`artifacts/listening_review/stage0_speech_vtl_warping_listening_pack/v2/`
  - 当前机器侧先验：`fail=8/8`，但 `effect` 高于 `v1`
  - 主观结果：更常可辨，但仍偏弱且 `slight artifact` 偏多
- 强约束顺序：
  - `1. LSF`
  - `2. VTL / tract-length warping`
  - 在这两步都没有形成正证据前，不再回到 `pole edit / cepstral delta` 微调
- 当前新增强约束：
  - `LSF / VTL` 到此都未形成足够正证据
  - 下一步不再继续抠经典 warp 局部参数
- `conditional_envelope_transport v1` 已进入可听审状态：
  - 配置：`experiments/stage0_baseline/v1_full/speech_conditional_envelope_transport_candidate_v1.json`
  - 入口：`scripts/open_stage0_speech_conditional_envelope_transport_review_gui.ps1 -PackVersion v1`
  - 正式包：`artifacts/listening_review/stage0_speech_conditional_envelope_transport_listening_pack/v1/`
  - 当前机器侧先验：`avg auto_quant_score ≈ 31.76`、`avg auto_effect_score ≈ 4.44`、`fail=8/8`
  - 主观结果：`8/8 reviewed`、`effect_audible no=8`
  - 当前判断：`v1` 已可收口为 `null_result`
- `conditional_envelope_transport v2` 已进入可听审状态：
  - 配置：`experiments/stage0_baseline/v1_full/speech_conditional_envelope_transport_candidate_v2.json`
  - 入口：`scripts/open_stage0_speech_conditional_envelope_transport_review_gui.ps1 -PackVersion v2`
  - 正式包：`artifacts/listening_review/stage0_speech_conditional_envelope_transport_listening_pack/v2/`
  - 当前机器侧先验：`avg auto_quant_score ≈ 35.64`、`avg auto_effect_score ≈ 9.63`、`fail=8/8`
  - 主观结果：`8/8 reviewed`、`effect_audible no=8`
  - 当前判断：reference-based conditional transport 到此已给出足够负证据，下一步不再继续出 `v3`
- `low-rank envelope subspace v1` 已进入可听审状态：
  - 配置：`experiments/stage0_baseline/v1_full/speech_low_rank_envelope_candidate_v1.json`
  - 入口：`scripts/open_stage0_speech_low_rank_envelope_review_gui.ps1 -PackVersion v1`
  - 正式包：`artifacts/listening_review/stage0_speech_low_rank_envelope_listening_pack/v1/`
  - 当前机器侧先验：`avg auto_quant_score ≈ 52.72`、`avg auto_direction_score ≈ 31.09`、`avg auto_effect_score ≈ 34.92`、`borderline=2`、`fail=6`
  - 主观结果：`8/8 reviewed`、`effect_audible no=8`
  - 当前判断：这条 learned latent 线虽强于 `conditional transport`，但最终仍不可辨识；下一步不再继续出常规 `v2`
- `neural envelope latent v1` 已进入可听审状态：
  - 配置：`experiments/stage0_baseline/v1_full/speech_neural_envelope_candidate_v1.json`
  - 入口：`scripts/open_stage0_speech_neural_envelope_review_gui.ps1 -PackVersion v1`
  - 正式包：`artifacts/listening_review/stage0_speech_neural_envelope_listening_pack/v1/`
  - 当前机器侧先验：`avg auto_quant_score ≈ 49.44`、`avg auto_direction_score ≈ 27.06`、`avg auto_effect_score ≈ 29.05`、`borderline=2`、`fail=6`
  - 主观结果：`8/8 reviewed`、`effect_audible no=8`
  - 当前判断：这条 nonlinear latent 线虽然已跑通，但最终仍不可辨识；下一步不再继续出常规 `v2`
- `conditioned neural envelope v1` 已进入可听审状态：
  - 配置：`experiments/stage0_baseline/v1_full/speech_conditioned_neural_envelope_candidate_v1.json`
  - 入口：`scripts/open_stage0_speech_conditioned_neural_envelope_review_gui.ps1 -PackVersion v1`
  - 正式包：`artifacts/listening_review/stage0_speech_conditioned_neural_envelope_listening_pack/v1/`
  - 当前机器侧先验：`avg auto_quant_score ≈ 38.48`、`avg auto_direction_score ≈ 11.45`、`avg auto_effect_score ≈ 13.29`、`fail=8`
  - 主观结果：`8/8 reviewed`、`effect_audible no=8`
  - 当前判断：这条 conditioned predictor 线方法层级更高，但最终仍不可辨识；下一步不再继续出常规 `v2`
- `probe-guided envelope v1` 已进入可听审状态：
  - 配置：`experiments/stage0_baseline/v1_full/speech_probe_guided_envelope_candidate_v1.json`
  - 入口：`scripts/open_stage0_speech_probe_guided_envelope_review_gui.ps1 -PackVersion v1`
  - 正式包：`artifacts/listening_review/stage0_speech_probe_guided_envelope_listening_pack/v1/`
  - 当前机器侧先验：`avg auto_quant_score ≈ 41.62`、`avg auto_direction_score ≈ 15.91`、`avg auto_effect_score ≈ 17.86`、`fail=8`
  - 主观结果：`8/8 reviewed`、`effect_audible no=8`
  - 当前判断：这条 direct residual 线方法层级更激进，但最终仍不可辨识；下一步不再继续出 `v2`
- `source-filter residual v1` 已进入可听审状态：
  - 配置：`experiments/stage0_baseline/v1_full/speech_source_filter_residual_candidate_v1.json`
  - 入口：`scripts/open_stage0_speech_source_filter_residual_review_gui.ps1 -PackVersion v1`
  - 正式包：`artifacts/listening_review/stage0_speech_source_filter_residual_listening_pack/v1/`
  - 当前机器侧先验：`avg auto_quant_score ≈ 39.19`、`avg auto_direction_score ≈ 12.70`、`avg auto_effect_score ≈ 13.89`、`fail=8`
  - 主观结果：`8/8 reviewed`、`effect_audible no=8`
  - 当前判断：这条线虽然升级到了 joint source/filter representation，但首轮仍不可辨识；后续不再继续扩大同档低先验包的人审覆盖
- `machine-first review gate v1` 已固定为当前流程默认：
  - 脚本：`scripts/build_listening_machine_gate_report.py`
  - 报告：`artifacts/machine_gate/v1/`
  - 当前 gate 阈值：`avg_auto_quant_score >= 65`、`avg_auto_direction_score >= 45`、`avg_auto_effect_score >= 45`，且 `top_auto_quant_score >= 75` 或 `strongish_rows >= 2`
  - 当前判断：gate 不通过的包，默认不再直接进正式人工听审
- `LSF v2` 已作为 machine-first 流程下首个晋级候选落地：
  - 配置：`experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v2.json`
  - sweep 入口：`scripts/run_lsf_machine_sweep.py`
  - sweep 总表：`experiments/stage0_baseline/v1_full/lsf_machine_sweep_v2/lsf_machine_sweep_pack_summary.csv`
  - 正式包：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v2/`
  - 入口：`scripts/open_stage0_speech_lsf_review_gui.ps1 -PackVersion v2`
  - 当前机器侧先验：`avg auto_quant_score = 78.85`、`avg auto_direction_score = 68.09`、`avg auto_effect_score = 73.71`
  - 当前主观结果：`8/8 reviewed`、`effect_audible yes=4 maybe=4 no=0`
  - 当前判断：这版已证明 `LSF` 不再是整包不可辨，但主结论仍是整体偏弱
- `LSF v3` 已作为下一拍正式候选落地：
  - 配置：`experiments/stage0_baseline/v1_full/speech_lsf_resonance_candidate_v3.json`
  - sweep 总表：`experiments/stage0_baseline/v1_full/lsf_machine_sweep_v3/lsf_machine_sweep_pack_summary.csv`
  - 正式包：`artifacts/listening_review/stage0_speech_lsf_listening_pack/v3/`
  - 入口：`scripts/open_stage0_speech_lsf_review_gui.ps1 -PackVersion v3`
  - 当前机器侧先验：`avg auto_quant_score = 82.81`、`avg auto_direction_score = 74.67`、`avg auto_effect_score = 78.63`、`fail=0`
  - 当前判断：这版是按 `v2` 的“偏弱 + 单点瞬时伪影”备注做的受控强化，下一步应直接正式听审

## 分支建议
- 如果后续开始多人或多任务并行，优先按任务边界拆分，而不是按文件类型拆分。
- 建议优先出现的分支方向：
  - `task/stage0-full-analysis`
  - `task/analysis-reporting`
  - `task/manifest-feature-expansion`
- 只有在出现真实分支后，才在这里登记“分支名 -> 任务 -> 涉及文件”的映射。
