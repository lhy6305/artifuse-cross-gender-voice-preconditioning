[CmdletBinding()]
param(
  [int]$MaxRows = 0
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "python.exe"
$manifestBuildScript = Join-Path $PSScriptRoot "build_stage1_rvc_cascade_manifest.py"
$batchRunScript = Join-Path $PSScriptRoot "run_stage1_rvc_cascade_batch.py"
$manifestCsv = Join-Path $repoRoot "artifacts\listening_review\stage1_rvc_cascade_eval\v1\rvc_cascade_manifest.csv"

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

if (-not (Test-Path $manifestCsv)) {
  Write-Host "Building stage1 RVC cascade manifest..."
  Invoke-Python -Arguments @($manifestBuildScript)
}

if ($MaxRows -gt 0) {
  Invoke-Python -Arguments @($batchRunScript, "--max-rows", "$MaxRows")
} else {
  Invoke-Python -Arguments @($batchRunScript)
}
