[CmdletBinding()]
param(
  [string[]]$Datasets = @("vctk", "libritts-r", "vocalset"),
  [string]$DataRoot = "data/datasets",
  [switch]$Force,
  [switch]$DryRun
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
    if ($DryRun) {
      Write-Host "[DRY-RUN] mkdir $Path"
    } else {
      New-Item -ItemType Directory -Force -Path $Path | Out-Null
    }
  }
}

function Invoke-CommandOrPrint {
  param(
    [string]$Label,
    [scriptblock]$Action
  )

  if ($DryRun) {
    Write-Host "[DRY-RUN] $Label"
  } else {
    & $Action
  }
}

function Remove-MacArtifacts {
  param([string]$Root)

  $macPaths = @(
    (Join-Path $Root "__MACOSX")
  )

  foreach ($path in $macPaths) {
    if (Test-Path -LiteralPath $path) {
      Invoke-CommandOrPrint -Label "remove $path" -Action {
        Remove-Item -LiteralPath $path -Recurse -Force
      }
    }
  }

  $dsStoreFiles = Get-ChildItem -LiteralPath $Root -Recurse -Force -Filter ".DS_Store" -ErrorAction SilentlyContinue
  foreach ($file in $dsStoreFiles) {
    Invoke-CommandOrPrint -Label "remove $($file.FullName)" -Action {
      Remove-Item -LiteralPath $file.FullName -Force
    }
  }
}

function Write-Marker {
  param([string]$MarkerPath)

  Invoke-CommandOrPrint -Label "write marker $MarkerPath" -Action {
    Set-Content -LiteralPath $MarkerPath -Encoding utf8 -Value ("extracted_at=" + (Get-Date).ToString("s"))
  }
}

function Expand-ZipWith7z {
  param(
    [string]$Archive,
    [string]$Destination
  )

  $sevenZip = Get-Command 7z.exe -ErrorAction Stop
  Invoke-CommandOrPrint -Label "7z x `"$Archive`" -o`"$Destination`" -aoa" -Action {
    & $sevenZip.Source x $Archive "-o$Destination" "-aoa" | Out-Host
    if ($LASTEXITCODE -ne 0) {
      throw "7z extraction failed: $Archive"
    }
  }
}

function Expand-TarGz {
  param(
    [string]$Archive,
    [string]$Destination
  )

  Invoke-CommandOrPrint -Label "tar -xf `"$Archive`" -C `"$Destination`"" -Action {
    tar -xf $Archive -C $Destination
    if ($LASTEXITCODE -ne 0) {
      throw "tar extraction failed: $Archive"
    }
  }
}

function Expand-IfNeeded {
  param(
    [string]$Label,
    [string]$Archive,
    [string]$Destination,
    [string]$Marker,
    [ValidateSet("zip", "targz")][string]$Type,
    [switch]$CleanupMacArtifacts
  )

  Ensure-Directory -Path $Destination

  if (-not (Test-Path -LiteralPath $Archive)) {
    throw "Archive not found: $Archive"
  }

  if ((Test-Path -LiteralPath $Marker) -and -not $Force) {
    Write-Host "Skip ${Label}: marker exists -> $Marker" -ForegroundColor Yellow
    return
  }

  Write-Host "Extract $Label"
  if ($Type -eq "zip") {
    Expand-ZipWith7z -Archive $Archive -Destination $Destination
  } else {
    Expand-TarGz -Archive $Archive -Destination $Destination
  }

  if ($CleanupMacArtifacts) {
    Remove-MacArtifacts -Root $Destination
  }

  Write-Marker -MarkerPath $Marker
}

function Expand-Vctk {
  param([string]$Root)

  $datasetDir = Join-Path $Root "speech/vctk"
  $archive = Join-Path $datasetDir "VCTK-Corpus-0.92.zip"
  $destination = Join-Path $datasetDir "raw/VCTK-Corpus-0.92"
  $marker = Join-Path $destination ".extract.ok"

  Write-Section "VCTK Corpus 0.92"
  Expand-IfNeeded `
    -Label "VCTK archive" `
    -Archive $archive `
    -Destination $destination `
    -Marker $marker `
    -Type "zip"
}

function Expand-LibriTtsR {
  param([string]$Root)

  $datasetDir = Join-Path $Root "speech/libritts_r"
  $rawRoot = Join-Path $datasetDir "raw"
  Ensure-Directory -Path $rawRoot

  Write-Section "LibriTTS-R"

  $items = @(
    @{ Label = "LibriTTS-R doc"; Archive = "doc.tar.gz"; Marker = ".extract.doc.ok" },
    @{ Label = "LibriTTS-R dev_clean"; Archive = "dev_clean.tar.gz"; Marker = ".extract.dev_clean.ok" },
    @{ Label = "LibriTTS-R test_clean"; Archive = "test_clean.tar.gz"; Marker = ".extract.test_clean.ok" }
  )

  foreach ($item in $items) {
    Expand-IfNeeded `
      -Label $item.Label `
      -Archive (Join-Path $datasetDir $item.Archive) `
      -Destination $rawRoot `
      -Marker (Join-Path $rawRoot $item.Marker) `
      -Type "targz"
  }
}

function Expand-VocalSet {
  param([string]$Root)

  $datasetDir = Join-Path $Root "singing/vocalset"
  $archive = Join-Path $datasetDir "VocalSet1-2.zip"
  $destination = Join-Path $datasetDir "raw/VocalSet1-2"
  $marker = Join-Path $destination ".extract.ok"

  Write-Section "VocalSet 1.2"
  Expand-IfNeeded `
    -Label "VocalSet archive" `
    -Archive $archive `
    -Destination $destination `
    -Marker $marker `
    -Type "zip" `
    -CleanupMacArtifacts
}

foreach ($dataset in $Datasets) {
  switch ($dataset.ToLowerInvariant()) {
    "vctk" { Expand-Vctk -Root $DataRoot }
    "libritts-r" { Expand-LibriTtsR -Root $DataRoot }
    "vocalset" { Expand-VocalSet -Root $DataRoot }
    default { throw "Unsupported dataset: $dataset" }
  }
}

Write-Host ""
Write-Host "Extraction plan completed." -ForegroundColor Green
