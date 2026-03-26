# Listening Review Artifacts

- 这里存放需要长期保留、便于问题追查的听审包与听审结果。
- 典型内容包括：
  - `original/` 与 `processed/` 音频副本
  - `listening_pack_summary.csv`
  - `listening_review_queue.csv`
  - `listening_review_quant_summary.md`
- 这里不再使用 `tmp/`，避免把正式听审资产误当成一次性临时文件。
- 按当前 `.gitignore` 规则，音频文件仍默认忽略，只保留本地；`csv` / `md` 等听审结论文件可以进入版本控制。
