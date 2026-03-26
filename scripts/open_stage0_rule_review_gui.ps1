[CmdletBinding()]
param(
  [switch]$Rebuild,
  [string]$PackVersion = "v1"
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "python.exe"
$buildScript = Join-Path $PSScriptRoot "build_stage0_rule_review_queue.py"
$guiScript = Join-Path $PSScriptRoot "stage0_rule_review_gui.py"
$packDir = Join-Path $repoRoot ("tmp\\stage0_rule_listening_pack\\" + $PackVersion)
$summaryCsv = Join-Path $packDir "listening_pack_summary.csv"
$queueCsv = Join-Path $packDir "listening_review_queue.csv"

if (-not (Test-Path $summaryCsv)) {
  throw "Missing listening pack summary: $summaryCsv"
}

$needBuild = $Rebuild -or (-not (Test-Path $queueCsv))

if (Test-Path $pythonExe) {
  if ($needBuild) {
    Write-Host "Building listening review queue..."
    & $pythonExe $buildScript --summary-csv $summaryCsv --output-csv $queueCsv --reuse-cache
  } else {
    Write-Host "Opening cached listening review queue..."
  }
  & $pythonExe $guiScript --csv $queueCsv
} else {
  if ($needBuild) {
    Write-Host "Building listening review queue..."
    python $buildScript --summary-csv $summaryCsv --output-csv $queueCsv --reuse-cache
  } else {
    Write-Host "Opening cached listening review queue..."
  }
  python $guiScript --csv $queueCsv
}
