[CmdletBinding()]
param(
  [ValidateSet("fixed_eval", "clean_speech")]
  [string]$InputMode = "fixed_eval",
  [int]$SamplesPerCell = 0,
  [int]$MaxRows = 0
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "python.exe"
$scriptPath = Join-Path $PSScriptRoot "run_representation_layer_probe.py"

if ($InputMode -eq "fixed_eval") {
  $inputCsv = Join-Path $repoRoot "experiments\fixed_eval\v1_2\fixed_eval_review_final_v1_2.csv"
  $outputDir = Join-Path $repoRoot "experiments\representation_layer\v1_fixed_eval_pilot"
} else {
  $inputCsv = Join-Path $repoRoot "data\datasets\_meta\utterance_manifest_clean_speech_v1.csv"
  $outputDir = Join-Path $repoRoot "experiments\representation_layer\v1_clean_speech_probe"
}

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

Invoke-Python -Arguments @(
  $scriptPath,
  "--input-csv", $inputCsv,
  "--output-dir", $outputDir,
  "--samples-per-cell", "$SamplesPerCell",
  "--max-rows", "$MaxRows"
)
