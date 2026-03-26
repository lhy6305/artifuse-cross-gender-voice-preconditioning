[CmdletBinding()]
param(
  [switch]$Rebuild,
  [int]$AutoCloseMs = 0
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "python.exe"
$packBuildScript = Join-Path $PSScriptRoot "build_stage0_speech_world_stft_delta_listening_pack.py"
$queueBuildScript = Join-Path $PSScriptRoot "build_stage0_rule_review_queue.py"
$guiScript = Join-Path $PSScriptRoot "stage0_rule_review_gui.py"
$ruleConfig = Join-Path $repoRoot "experiments\stage0_baseline\v1_full\speech_world_stft_delta_candidate_v1.json"
$packDir = Join-Path $repoRoot "tmp\stage0_speech_world_stft_delta_listening_pack\v1"
$summaryCsv = Join-Path $packDir "listening_pack_summary.csv"
$queueCsv = Join-Path $packDir "listening_review_queue.csv"
$summaryMd = Join-Path $packDir "listening_review_quant_summary.md"

Write-Host "Using speech WORLD-guided STFT delta listening pack:" $packDir

function Invoke-Python {
  param(
    [string[]]$Arguments
  )

  if (Test-Path $pythonExe) {
    & $pythonExe @Arguments
  } else {
    python @Arguments
  }
}

if (-not (Test-Path $summaryCsv)) {
  Write-Host "Building speech WORLD-guided STFT delta listening pack..."
  Invoke-Python -Arguments @($packBuildScript)
}

if (-not (Test-Path $summaryCsv)) {
  throw "Missing speech WORLD-guided STFT delta listening pack summary after build: $summaryCsv"
}

$needQueue = $Rebuild -or (-not (Test-Path $queueCsv))
if ($needQueue) {
  Write-Host "Building speech WORLD-guided STFT delta listening review queue..."
  Invoke-Python -Arguments @(
    $queueBuildScript,
    "--rule-config", $ruleConfig,
    "--summary-csv", $summaryCsv,
    "--output-csv", $queueCsv,
    "--summary-md", $summaryMd,
    "--reuse-cache"
  )
} else {
  Write-Host "Opening cached speech WORLD-guided STFT delta listening review queue..."
}

if (-not (Test-Path $queueCsv)) {
  throw "Missing speech WORLD-guided STFT delta listening review queue: $queueCsv"
}

if ($AutoCloseMs -gt 0) {
  Invoke-Python -Arguments @($guiScript, "--csv", $queueCsv, "--auto-close-ms", "$AutoCloseMs")
} else {
  Invoke-Python -Arguments @($guiScript, "--csv", $queueCsv)
}
