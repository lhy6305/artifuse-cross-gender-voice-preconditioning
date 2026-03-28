# Documentation Language And Encoding Policy v1

## Purpose

This policy keeps active project docs stable under the current Windows and PowerShell environment.

## Active Doc Language Rule

- Active living docs must use English only.
- Active living docs must use ASCII only.
- Historical docs and archive docs may remain unchanged until they become active again.
- Once a historical doc becomes active, migrate it to English ASCII before further maintenance.

## Active Doc Set

The current active doc set is defined in `docs/00_context_bootstrap.md`.

## Read Rule

- Repo text files are UTF-8.
- In PowerShell, always read text with `-Encoding utf8`.
- If text appears garbled, suspect a default-code-page read before suspecting file corruption.

## Write Rule

- Do not use PowerShell text write cmdlets for active repo docs.
- In this environment, PowerShell UTF-8 writes may add a BOM.
- Use repo-safe edit paths that preserve UTF-8 without BOM.

## User Reply Rule

- This policy applies to repo docs only.
- User-facing assistant replies must remain in Simplified Chinese, regardless of the language used in docs.

## Remediation Rule

If a doc appears corrupted:

1. Verify the raw bytes first.
2. Reopen with explicit UTF-8.
3. Remove mojibake from the text layer.
4. Keep the repaired file in English ASCII if it is an active living doc.
