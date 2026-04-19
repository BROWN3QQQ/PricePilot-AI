param(
    [string]$Timerange = "20240101-",
    [string]$Strategy = "BinanceSpotLowFrequencyStrategy",
    [int]$Epochs = 200,
    [switch]$SkipDownload,
    [switch]$SkipHyperopt,
    [switch]$SkipValidation
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot

if (-not $SkipDownload) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repoRoot "scripts\download_data.ps1") `
        -Timerange $Timerange
}

& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repoRoot "scripts\run_backtest.ps1") `
    -Timerange $Timerange `
    -Strategy $Strategy `
    -Notes "research_cycle_backtest"

if (-not $SkipHyperopt) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repoRoot "scripts\run_hyperopt.ps1") `
        -Timerange $Timerange `
        -Strategy $Strategy `
        -Epochs $Epochs
}

if (-not $SkipValidation) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repoRoot "scripts\validate_strategy.ps1") `
        -Timerange $Timerange `
        -Strategy $Strategy
}
