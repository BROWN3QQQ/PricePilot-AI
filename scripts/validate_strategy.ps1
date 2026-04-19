param(
    [string]$Timerange = "20240101-",
    [string]$Strategy = "BinanceSpotLowFrequencyStrategy",
    [string]$TimeframeDetail = "15m"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra\docker-compose.yml"
$reportDir = Join-Path $repoRoot "reports\backtests"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$validationLog = Join-Path $reportDir "$timestamp-$Strategy-validation.log"
$baseArgs = @(
    "-f", $composeFile,
    "run", "--rm", "--no-deps", "freqtrade-dryrun"
)
$configArgs = @(
    "--config", "/freqtrade/config/base.spot.json",
    "--config", "/freqtrade/config/dryrun.json",
    "--strategy", $Strategy,
    "--timerange", $Timerange,
    "--timeframe-detail", $TimeframeDetail
)

if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

& powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $repoRoot "scripts\run_backtest.ps1") `
    -Timerange $Timerange `
    -Strategy $Strategy `
    -TimeframeDetail $TimeframeDetail `
    -Notes "validation_backtest" 2>&1 | Tee-Object -FilePath $validationLog

& docker compose @baseArgs "lookahead-analysis" @configArgs 2>&1 | Tee-Object -FilePath $validationLog -Append
& docker compose @baseArgs "recursive-analysis" @configArgs 2>&1 | Tee-Object -FilePath $validationLog -Append

Write-Host "Validation log: $validationLog"
