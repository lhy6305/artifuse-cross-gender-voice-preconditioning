param(
    [ValidateSet('all', 'speech', 'singing', 'finalize')]
    [string]$Step = 'all',
    [string]$OutputDir = 'experiments/stage0_baseline/v1_full',
    [int]$Jobs = 0,
    [int]$BatchSize = 64,
    [int]$ProgressEvery = 50,
    [int]$MaxRows = 0,
    [switch]$Overwrite,
    [switch]$Pilot
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [Console]::OutputEncoding

if ($Jobs -le 0) {
    $Jobs = [Math]::Max(1, [Environment]::ProcessorCount / 1)
}

$args = @(
    '.\scripts\run_stage0_baseline_analysis.py',
    '--output-dir', $OutputDir,
    '--jobs', $Jobs,
    '--batch-size', $BatchSize,
    '--progress-every', $ProgressEvery
)

if ($Pilot) {
    $args += '--pilot'
}

if ($MaxRows -gt 0) {
    $args += @('--max-rows', $MaxRows)
}

if ($Overwrite) {
    $args += '--overwrite'
}

switch ($Step) {
    'speech' {
        $args += @('--subset', 'speech')
    }
    'singing' {
        $args += @('--subset', 'singing')
    }
    'all' {
        $args += @('--subset', 'all')
    }
    'finalize' {
        $args += '--finalize-only'
    }
}
cd ..
& .\python.exe @args
