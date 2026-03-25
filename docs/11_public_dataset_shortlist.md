# 公开数据集候选与下载命令

## 结论先行

当前阶段最适合本项目的公开数据集组合是：

1. `VCTK Corpus 0.92`
   - 用途：高质量 `speech` 主数据集
   - 协议：`CC BY 4.0`
   - 适配性：录音质量高、多人、多性别，适合做最干净的 `speech` 主分析集

2. `LibriTTS-R`
   - 用途：第二套 `speech` 数据集，用于扩展规模和做跨数据集一致性检查
   - 协议：`CC BY 4.0`
   - 适配性：多说话人、规模大、官方文档完整；但风格偏有声书朗读，不如 VCTK 统一

3. `VocalSet 1.2`
   - 用途：主 `singing` 补充数据集
   - 协议：`CC BY 4.0`
   - 适配性：公开可下、单声部、20 位歌手，其中 9 男 11 女，最贴近当前“公开可用 + 男女都有 + vocal-only”的需求
   - 局限：更偏 vocalise / technique / excerpt，不是流行歌曲整曲语料

4. `OpenCpop`
   - 用途：可选补充，不作为当前主数据集
   - 协议：`CC BY-NC 4.0`
   - 适配性：中文、录音质量高、标注完整
   - 局限：仅女性、仅 5.2 小时、非商业限制明显，因此不适合做当前项目的主唱歌语料

## 协议判断

### 可直接作为当前项目主力候选
- `VCTK Corpus 0.92`：`CC BY 4.0`
- `LibriTTS-R`：`CC BY 4.0`
- `VocalSet 1.2`：`CC BY 4.0`

这三套都适合当前 MIT 协议仓库配套使用，但要注意：
- 数据集本身不等于仓库协议；
- 训练、导出、发布样例或派生产物时，仍需保留相应 attribution；
- 若后续公开发布模型或音频样例，必须再核对各数据集的具体 attribution 要求。

### 仅作可选补充
- `OpenCpop`：`CC BY-NC 4.0`

这意味着：
- 可用于非商业研究和本地实验；
- 不适合作为默认主数据集；
- 若未来有商业化或更宽松分发目标，应避免把它混进主训练链。

## 推荐准备顺序

### 第一批，建议先下
1. `VCTK Corpus 0.92`
2. `LibriTTS-R` 的 `doc.tar.gz`
3. `LibriTTS-R` 的 `dev_clean` 或 `test_clean`
4. `VocalSet 1.2`

### 第二批，视需求再下
1. `LibriTTS-R` 的更多 split
2. `OpenCpop`

## 官方来源

### VCTK Corpus 0.92
- 官方页面：
  - <https://datashare.ed.ac.uk/handle/10283/3443>
- 许可证文本：
  - <https://datashare.ed.ac.uk/bitstream/handle/10283/3443/license_text.txt?sequence=6&isAllowed=y>
- README：
  - <https://datashare.ed.ac.uk/bitstream/handle/10283/3443/README.txt?sequence=1&isAllowed=y>
- 数据包直链：
  - <https://datashare.ed.ac.uk/bitstream/handle/10283/3443/VCTK-Corpus-0.92.zip?sequence=2&isAllowed=y>

### LibriTTS-R
- 官方页面：
  - <https://openslr.org/141/>
- 文档包：
  - <https://openslr.magicdatatech.com/resources/141/doc.tar.gz>
- 常用 split：
  - <https://openslr.magicdatatech.com/resources/141/dev_clean.tar.gz>
  - <https://openslr.magicdatatech.com/resources/141/test_clean.tar.gz>
  - <https://openslr.magicdatatech.com/resources/141/train_clean_100.tar.gz>

### VocalSet 1.2
- 官方记录页：
  - <https://zenodo.org/records/1442513>
- API 记录：
  - <https://zenodo.org/api/records/1442513>
- 最新版数据包：
  - <https://zenodo.org/api/records/1442513/files/VocalSet1-2.zip/content>

### OpenCpop
- 官方主页：
  - <https://wenet-e2e.github.io/opencpop/>
- 下载页：
  - <https://wenet-e2e.github.io/opencpop/download/>
- 许可证说明页：
  - <https://wenet-e2e.github.io/opencpop/liscense/>

## PowerShell 下载命令

先统一编码：

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding
```

创建目录：

```powershell
New-Item -ItemType Directory -Force -Path `
  data\datasets\speech\vctk, `
  data\datasets\speech\libritts_r, `
  data\datasets\singing\vocalset, `
  data\datasets\optional\opencpop
```

下载 `VCTK`：

```powershell
curl.exe -L -k `
  "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/README.txt?sequence=1&isAllowed=y" `
  -o data\datasets\speech\vctk\README.txt

curl.exe -L -k `
  "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/license_text.txt?sequence=6&isAllowed=y" `
  -o data\datasets\speech\vctk\license_text.txt

curl.exe -L -k -C - `
  "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/VCTK-Corpus-0.92.zip?sequence=2&isAllowed=y" `
  -o data\datasets\speech\vctk\VCTK-Corpus-0.92.zip
```

下载 `LibriTTS-R`：

```powershell
curl.exe -L -k -C - `
  "https://openslr.magicdatatech.com/resources/141/doc.tar.gz" `
  -o data\datasets\speech\libritts_r\doc.tar.gz

curl.exe -L -k -C - `
  "https://openslr.magicdatatech.com/resources/141/dev_clean.tar.gz" `
  -o data\datasets\speech\libritts_r\dev_clean.tar.gz

curl.exe -L -k -C - `
  "https://openslr.magicdatatech.com/resources/141/test_clean.tar.gz" `
  -o data\datasets\speech\libritts_r\test_clean.tar.gz
```

下载 `VocalSet 1.2`：

```powershell
curl.exe -L `
  "https://zenodo.org/api/records/1442513" `
  -o data\datasets\singing\vocalset\record.json

curl.exe -L -C - `
  "https://zenodo.org/api/records/1442513/files/VocalSet1-2.zip/content" `
  -o data\datasets\singing\vocalset\VocalSet1-2.zip
```

如果需要旧版较小包，可选：

```powershell
curl.exe -L -C - `
  "https://zenodo.org/api/records/1442513/files/VocalSet11.zip/content" `
  -o data\datasets\singing\vocalset\VocalSet11.zip
```

## 解压命令

```powershell
tar -xf data\datasets\speech\libritts_r\doc.tar.gz -C data\datasets\speech\libritts_r
tar -xf data\datasets\speech\libritts_r\dev_clean.tar.gz -C data\datasets\speech\libritts_r
tar -xf data\datasets\speech\libritts_r\test_clean.tar.gz -C data\datasets\speech\libritts_r

7z x data\datasets\speech\vctk\VCTK-Corpus-0.92.zip -odata\datasets\speech\vctk
7z x data\datasets\singing\vocalset\VocalSet1-2.zip -odata\datasets\singing\vocalset
```

## 下载后第一步检查

### VCTK
- 看 `speaker-info.txt`、录音目录、麦克风版本
- 优先使用高质量麦克风版本

### LibriTTS-R
- 解开 `doc.tar.gz` 后重点看：
  - `speakers.tsv`
  - `README_libritts_r.txt`
  - `LICENSE.txt`

### VocalSet
- 重点看：
  - `readme-anon.txt`
  - singer 到 voice type 的映射
  - train/test singer 划分文件

## 当前建议

若你要尽快开跑第一轮分析，建议采用：

1. `VCTK` 作为高质量 `speech` 主集
2. `LibriTTS-R dev_clean + test_clean` 作为第二 `speech` 集
3. `VocalSet 1.2` 作为第一 `singing` 集

这样已经足够支撑：
- `speech` / `singing` 分域分析
- 男女差异统计
- 跨数据集一致性检查
- 第一版固定评测集抽样
