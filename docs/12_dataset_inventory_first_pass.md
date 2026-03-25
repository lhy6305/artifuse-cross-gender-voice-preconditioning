# 数据资产首轮盘点

## 本轮输出
- 资产总表：`data/datasets/_meta/dataset_inventory.csv`
- 片段清单：`data/datasets/_meta/utterance_manifest.csv`
- 盘点脚本：`scripts/build_dataset_inventory.py`
- manifest 脚本：`scripts/build_utterance_manifest.py`

## 当前本地数据概览

| 数据集 | 本地使用范围 | 域 | 说话人/歌手 | 男 | 女 | 时长（小时） | 样本数 | 采样率 |
|---|---|---|---:|---:|---:|---:|---:|---:|
| VCTK Corpus 0.92 | `wav48_silence_trimmed/*_mic1.flac` | speech | 110 | 47 | 63 | 41.62 | 44455 | 48000 |
| LibriTTS-R | `dev-clean + test-clean` | speech | 79 | 40 | 39 | 17.47 | 10573 | 24000 |
| VocalSet 1.2 | `data_by_singer` | singing | 20 | 11 | 9 | 8.79 | 3613 | 44100 |

## 本轮关键观察

### 1. speech 主数据已经足够启动第一轮分析
- `VCTK` 单独就能承担第一轮高质量 `speech` 主分析集。
- `LibriTTS-R` 目前本地只解了 `dev-clean + test-clean`，但已经足够做一轮跨数据集一致性检查。

### 2. singing 数据目前以 VocalSet 为主
- `VocalSet` 是当前本地唯一成体系、公开可用、男女都覆盖的 `singing` 数据。
- 它适合做第一轮 singing 差异分析，但要注意其内容以 vocalise / technique / excerpt 为主，不是通俗歌曲整句主唱场景。

### 3. 本地统计边界已经固定
- `VCTK` 只统计 `mic1.flac`，避免和 `mic2` 重复。
- `VocalSet` 只统计 `data_by_singer`，避免和 `data_by_technique`、`data_by_vowel` 三重重复。

## 当前决策

第一轮主分析集建议采用：

1. `VCTK` 作为高质量 `speech` 主集
2. `VocalSet` 作为 `singing` 主集
3. `LibriTTS-R` 作为第二 `speech` 集，用于检查规则是否只在单一数据集上成立

## 下一步

1. 对 `VCTK` 和 `VocalSet` 抽样做基础质量巡检。
2. 明确第一轮固定评测集抽样规则。
3. 扩展 `utterance_manifest`，补更多筛选字段。
