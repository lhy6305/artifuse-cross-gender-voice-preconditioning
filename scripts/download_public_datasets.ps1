[CmdletBinding()]
param(
  [string[]]$Datasets = @("vctk", "libritts-r", "vocalset"),
  [string]$DataRoot = "data/datasets",
  [int]$RetryCount = 5,
  [int]$RetryDelaySeconds = 15,
  [switch]$MetadataOnly
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

function Write-Section {
  param([string]$Message)
  Write-Host ""
  Write-Host "== $Message ==" -ForegroundColor Cyan
}

function Ensure-Directory {
  param([string]$Path)
  if (-not (Test-Path -LiteralPath $Path)) {
    New-Item -ItemType Directory -Force -Path $Path | Out-Null
  }
}

function Get-FileMd5 {
  param([string]$Path)
  (Get-FileHash -LiteralPath $Path -Algorithm MD5).Hash.ToLowerInvariant()
}

function Invoke-ResumableDownload {
  param(
    [Parameter(Mandatory = $true)][string]$Url,
    [Parameter(Mandatory = $true)][string]$Destination,
    [string]$ExpectedMd5,
    [Nullable[long]]$ExpectedSize = $null,
    [switch]$InsecureTls
  )

  Ensure-Directory -Path (Split-Path -Parent $Destination)

  $curlArgs = @("-L", "-C", "-", "--fail", "--output", $Destination)
  if ($InsecureTls) {
    $curlArgs += "-k"
  }
  $curlArgs += $Url

  $attempt = 0
  while ($true) {
    $attempt++
    Write-Host "Downloading: $Destination"
    Write-Host "Attempt $attempt/$RetryCount"
    & curl.exe @curlArgs
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
      break
    }

    if ($attempt -ge $RetryCount) {
      throw "Download failed after $RetryCount attempts: $Url"
    }

    Write-Warning "curl exited with code $exitCode. Retrying in $RetryDelaySeconds seconds."
    Start-Sleep -Seconds $RetryDelaySeconds
  }

  if ($ExpectedSize -and (Test-Path -LiteralPath $Destination)) {
    $actualSize = (Get-Item -LiteralPath $Destination).Length
    if ($actualSize -ne $ExpectedSize) {
      throw "Size mismatch for $Destination. Expected $ExpectedSize bytes, got $actualSize bytes."
    }
  }

  if ($ExpectedMd5) {
    $actualMd5 = Get-FileMd5 -Path $Destination
    if ($actualMd5 -ne $ExpectedMd5.ToLowerInvariant()) {
      throw "MD5 mismatch for $Destination. Expected $ExpectedMd5, got $actualMd5."
    }
    Write-Host "MD5 OK: $Destination" -ForegroundColor Green
  } else {
    Write-Warning "No official MD5 available for $Destination. Skipping hash verification."
  }
}

function Get-LibriTtsMd5Map {
  param([string]$DatasetDir)

  $md5Path = Join-Path $DatasetDir "md5sum.txt"
  Invoke-ResumableDownload `
    -Url "https://openslr.magicdatatech.com/resources/141/md5sum.txt" `
    -Destination $md5Path `
    -InsecureTls

  $map = @{}
  foreach ($line in Get-Content -LiteralPath $md5Path -Encoding utf8) {
    if ($line -match "^\s*([0-9a-fA-F]{32})\s+(.+?)\s*$") {
      $map[$matches[2]] = $matches[1].ToLowerInvariant()
    }
  }
  return $map
}

function Get-VocalSetRecord {
  param([string]$DatasetDir)

  $recordPath = Join-Path $DatasetDir "record.json"
  Invoke-ResumableDownload `
    -Url "https://zenodo.org/api/records/1442513" `
    -Destination $recordPath

  return Get-Content -LiteralPath $recordPath -Encoding utf8 | ConvertFrom-Json
}

function Download-Vctk {
  param([string]$Root)

  $datasetDir = Join-Path $Root "speech/vctk"
  Ensure-Directory -Path $datasetDir
  Write-Section "VCTK Corpus 0.92"

  Invoke-ResumableDownload `
    -Url "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/README.txt?sequence=1&isAllowed=y" `
    -Destination (Join-Path $datasetDir "README.txt") `
    -ExpectedMd5 "31b61beec43565e27237dbb738566a7a" `
    -InsecureTls

  Invoke-ResumableDownload `
    -Url "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/license_text.txt?sequence=6&isAllowed=y" `
    -Destination (Join-Path $datasetDir "license_text.txt") `
    -InsecureTls

  if (-not $MetadataOnly) {
    Invoke-ResumableDownload `
      -Url "https://datashare.ed.ac.uk/bitstream/handle/10283/3443/VCTK-Corpus-0.92.zip?sequence=2&isAllowed=y" `
      -Destination (Join-Path $datasetDir "VCTK-Corpus-0.92.zip") `
      -ExpectedMd5 "8a6ba2946b36fcbef0212cad601f4bfa" `
      -ExpectedSize 11747302977 `
      -InsecureTls
  }
}

function Download-LibriTtsR {
  param([string]$Root)

  $datasetDir = Join-Path $Root "speech/libritts_r"
  Ensure-Directory -Path $datasetDir
  Write-Section "LibriTTS-R"

  $md5Map = Get-LibriTtsMd5Map -DatasetDir $datasetDir
  $files = @(
    @{ Name = "doc.tar.gz"; Url = "https://openslr.magicdatatech.com/resources/141/doc.tar.gz" },
    @{ Name = "dev_clean.tar.gz"; Url = "https://openslr.magicdatatech.com/resources/141/dev_clean.tar.gz" },
    @{ Name = "test_clean.tar.gz"; Url = "https://openslr.magicdatatech.com/resources/141/test_clean.tar.gz" }
  )

  foreach ($file in $files) {
    if ($MetadataOnly -and $file.Name -ne "doc.tar.gz") {
      continue
    }

    $expectedMd5 = $null
    if ($md5Map.ContainsKey($file.Name)) {
      $expectedMd5 = $md5Map[$file.Name]
    }

    Invoke-ResumableDownload `
      -Url $file.Url `
      -Destination (Join-Path $datasetDir $file.Name) `
      -ExpectedMd5 $expectedMd5 `
      -InsecureTls
  }
}

function Download-VocalSet {
  param([string]$Root)

  $datasetDir = Join-Path $Root "singing/vocalset"
  Ensure-Directory -Path $datasetDir
  Write-Section "VocalSet 1.2"

  $record = Get-VocalSetRecord -DatasetDir $datasetDir
  $targetFile = $record.files | Where-Object { $_.key -eq "VocalSet1-2.zip" } | Select-Object -First 1
  if (-not $targetFile) {
    throw "Could not find VocalSet1-2.zip in Zenodo record metadata."
  }

  $expectedMd5 = $null
  if ($targetFile.checksum -match "^md5:(.+)$") {
    $expectedMd5 = $matches[1]
  }

  if (-not $MetadataOnly) {
    Invoke-ResumableDownload `
      -Url "https://zenodo.org/api/records/1442513/files/VocalSet1-2.zip/content" `
      -Destination (Join-Path $datasetDir "VocalSet1-2.zip") `
      -ExpectedMd5 $expectedMd5 `
      -ExpectedSize ([long]$targetFile.size)
  }
}

Ensure-Directory -Path $DataRoot

foreach ($dataset in $Datasets) {
  switch ($dataset.ToLowerInvariant()) {
    "vctk" { Download-Vctk -Root $DataRoot }
    "libritts-r" { Download-LibriTtsR -Root $DataRoot }
    "vocalset" { Download-VocalSet -Root $DataRoot }
    default { throw "Unsupported dataset: $dataset" }
  }
}

Write-Host ""
Write-Host "All requested downloads completed." -ForegroundColor Green
