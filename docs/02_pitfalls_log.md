# Pitfalls Log

## Active Global Pitfalls

### 1. PowerShell reads are unsafe without explicit UTF-8

- Problem: PowerShell may decode UTF-8 text through the local code page if encoding is not specified.
- Impact: correct files may appear garbled and may be edited incorrectly afterward.
- Rule: always read repo text with explicit UTF-8.

### 2. PowerShell text writes are not trusted for repo docs

- Problem: PowerShell UTF-8 text writes may add a BOM in this environment.
- Impact: active docs may gain noisy headers and inconsistent byte format.
- Rule: do not use PowerShell text write cmdlets for repo doc edits.

### 3. Active docs and user replies follow different language rules

- Problem: the user works in Chinese, while active docs must stay English ASCII.
- Impact: doc maintenance can drift into the wrong language unless the two channels stay separate.
- Rule: keep active docs in English ASCII, and keep user-facing replies in Simplified Chinese.

### 4. Heavy local assets and local work dirs must stay outside Git

- Problem: model weights, indexes, raw audio, dataset archives, and local work dirs are easy to stage by accident.
- Impact: Git history can become heavy, noisy, or unsafe.
- Rule: keep those assets ignored by default and keep only lightweight recoverable artifacts in Git.

### 5. Use stable `record_id`, not `utt_id`, for joins

- Problem: `utt_id` is not globally unique in the full manifest.
- Impact: cache joins and resume logic can silently misalign records.
- Rule: use stable `record_id` for joins, cache keys, and resume logic.

### 6. Use repo root `.\python.exe` for project scripts

- Problem: mixing in system Python can break local import assumptions and runtime consistency.
- Impact: build and analysis scripts may fail or drift across sessions.
- Rule: use repo root `.\python.exe` unless a task explicitly documents a different interpreter.

## Archived Historical Pitfalls

Historical and resolved setup-specific pitfalls were moved out of this active handoff file into:

- `docs/68_archive_historical_pitfalls_from_old_02_v1.md`
