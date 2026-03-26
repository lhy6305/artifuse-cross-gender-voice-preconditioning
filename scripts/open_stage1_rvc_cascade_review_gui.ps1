[CmdletBinding()]
param(
  [int]$AutoCloseMs = 0
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "python.exe"
$queueBuildScript = Join-Path $PSScriptRoot "build_stage1_rvc_cascade_review_queue.py"
$guiScript = Join-Path $PSScriptRoot "stage0_rule_review_gui.py"
$queueCsv = Join-Path $repoRoot "tmp\stage1_rvc_cascade_eval\v1\rvc_cascade_review_queue.csv"

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

if (-not (Test-Path $queueCsv)) {
  Write-Host "Building stage1 RVC cascade review queue..."
  Invoke-Python -Arguments @($queueBuildScript)
}

if ($AutoCloseMs -gt 0) {
  Invoke-Python -Arguments @($guiScript, "--csv", $queueCsv, "--auto-close-ms", "$AutoCloseMs")
} else {
  Invoke-Python -Arguments @($guiScript, "--csv", $queueCsv)
}
