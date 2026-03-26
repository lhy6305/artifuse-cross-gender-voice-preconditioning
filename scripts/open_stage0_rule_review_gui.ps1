[CmdletBinding()]
param(
  [switch]$Rebuild,
  [string]$PackVersion = "v1",
  [int]$AutoCloseMs = 0
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonExe = Join-Path $repoRoot "python.exe"
$buildScript = Join-Path $PSScriptRoot "build_stage0_rule_review_queue.py"
$guiScript = Join-Path $PSScriptRoot "stage0_rule_review_gui.py"

function Set-FallbackArgsFromList {
  param(
    [object[]]$ArgList
  )

  if (-not $ArgList) {
    return
  }

  for ($i = 0; $i -lt $ArgList.Count; $i++) {
    $value = [string]$ArgList[$i]
    if ($value -ieq "-PackVersion" -and ($i + 1) -lt $ArgList.Count) {
      $script:PackVersion = [string]$ArgList[$i + 1]
    }
    if ($value -ieq "-Rebuild") {
      $script:Rebuild = $true
    }
    if ($value -ieq "-AutoCloseMs" -and ($i + 1) -lt $ArgList.Count) {
      $script:AutoCloseMs = [int]$ArgList[$i + 1]
    }
  }
}

Set-FallbackArgsFromList -ArgList $MyInvocation.UnboundArguments
Set-FallbackArgsFromList -ArgList $args

if ($MyInvocation.Line) {
  $line = [string]$MyInvocation.Line
  $packMatch = [regex]::Match($line, '(?i)-PackVersion\s+("?)([A-Za-z0-9_\-\.]+)\1')
  if ($packMatch.Success) {
    $PackVersion = $packMatch.Groups[2].Value
  }
  if ($line -match '(?i)(?:^|\s)-Rebuild(?:\s|$)') {
    $Rebuild = $true
  }
  $closeMatch = [regex]::Match($line, '(?i)-AutoCloseMs\s+(\d+)')
  if ($closeMatch.Success) {
    $AutoCloseMs = [int]$closeMatch.Groups[1].Value
  }
}

$packDir = Join-Path $repoRoot (Join-Path "artifacts\listening_review\stage0_rule_listening_pack" $PackVersion)
$summaryCsv = Join-Path $packDir "listening_pack_summary.csv"
$queueCsv = Join-Path $packDir "listening_review_queue.csv"

Write-Host "Using listening pack:" $packDir

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
  if ($AutoCloseMs -gt 0) {
    & $pythonExe $guiScript --csv $queueCsv --auto-close-ms $AutoCloseMs
  } else {
    & $pythonExe $guiScript --csv $queueCsv
  }
} else {
  if ($needBuild) {
    Write-Host "Building listening review queue..."
    python $buildScript --summary-csv $summaryCsv --output-csv $queueCsv --reuse-cache
  } else {
    Write-Host "Opening cached listening review queue..."
  }
  if ($AutoCloseMs -gt 0) {
    python $guiScript --csv $queueCsv --auto-close-ms $AutoCloseMs
  } else {
    python $guiScript --csv $queueCsv
  }
}
