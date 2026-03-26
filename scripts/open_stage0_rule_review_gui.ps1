[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "python.exe"
$buildScript = Join-Path $PSScriptRoot "build_stage0_rule_review_queue.py"
$guiScript = Join-Path $PSScriptRoot "stage0_rule_review_gui.py"
$summaryCsv = Join-Path $repoRoot "tmp\\stage0_rule_listening_pack\\v1\\listening_pack_summary.csv"
$queueCsv = Join-Path $repoRoot "tmp\\stage0_rule_listening_pack\\v1\\listening_review_queue.csv"

if (-not (Test-Path $summaryCsv)) {
  throw "Missing listening pack summary: $summaryCsv"
}

if (Test-Path $pythonExe) {
  & $pythonExe $buildScript --summary-csv $summaryCsv --output-csv $queueCsv
  & $pythonExe $guiScript --csv $queueCsv
} else {
  python $buildScript --summary-csv $summaryCsv --output-csv $queueCsv
  python $guiScript --csv $queueCsv
}
