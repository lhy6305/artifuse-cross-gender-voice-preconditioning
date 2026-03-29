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

### 7. PowerShell inline Python patch scripts fail with nested quotes

- Problem: PowerShell `-c "..."` inline strings mangle nested double quotes and produce SyntaxError.
- Impact: patch scripts written inline fail before running any code.
- Rule: write patch scripts to a file using `[System.IO.File]::WriteAllText(path, content, UTF8)`,
  then run them as a separate step with `.\python.exe .\tmp\patch_name.py`.

### 8. LPC fit objective must use utterance-level prototype, not per-frame ATRR target

- Problem: comparing LPC carrier envelope against per-frame ATRR mel target distributions fails
  because LPC produces smooth envelopes while mel ATRR targets have sharp per-frame structure.
  The fit objective can never improve on the original and no frames are accepted.
- Impact: near-zero fit success rate, reconstruction produces no audible change.
- Rule: use the utterance-level weighted target-gender prototype as the fit objective target.
  Per-frame ATRR targets are for edit direction only, not for acceptance testing.

### 9. Highband error weight in LSF fit objective must be small

- Problem: the highband log-power error term is on the order of 0.29 to 0.35 per frame for
  the feminine direction (which legitimately raises energy). A weight of 0.08 adds 0.024 to
  0.028 to the objective per frame, wiping out fit+core improvement and rejecting valid edits.
- Impact: near-zero fit success rate for the feminine direction.
- Rule: keep the highband penalty weight at 0.005 or lower in the LSF fit objective.
  Highband preservation is already handled through the synthesis blend path.

### 10. mel distribution local_strength normalization must be relative, not absolute

- Problem: using a hardcoded absolute divisor (e.g. 0.12) for local_strength when distributions
  sum to 1.0 across 80 bins produces near-zero strength values (actual slice deltas are 0.001 to 0.03).
- Impact: all dynamic edits collapse to near-identity, zero audible change.
- Rule: normalize local_strength by the maximum possible mass for the slice
  (slice bin count / total bins) rather than a hardcoded constant.

## Archived Historical Pitfalls

Historical and resolved setup-specific pitfalls were moved out of this active handoff file into:

- `docs/68_archive_historical_pitfalls_from_old_02_v1.md`