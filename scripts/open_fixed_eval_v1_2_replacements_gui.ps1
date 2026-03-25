[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "python.exe"
$guiScript = Join-Path $PSScriptRoot "fixed_eval_review_gui.py"
$queueCsv = Join-Path $repoRoot "experiments\\fixed_eval\\v1_2\\review_pack\\replacements_only_queue_v1_2.csv"

if (Test-Path $pythonExe) {
  & $pythonExe $guiScript --csv $queueCsv
} else {
  python $guiScript --csv $queueCsv
}
