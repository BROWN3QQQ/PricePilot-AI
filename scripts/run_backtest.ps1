param(
    [string]$Timerange = "20240101-",
    [string]$Strategy = "BinanceSpotLowFrequencyStrategy",
    [string]$TimeframeDetail = "15m",
    [string]$Notes = "manual_backtest"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra\docker-compose.yml"
$reportDir = Join-Path $repoRoot "reports\backtests"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$stdoutPath = Join-Path $reportDir "$timestamp-$Strategy-backtest.log"
$markdownPath = Join-Path $reportDir "$timestamp-$Strategy-backtest.md"
$artifactDir = Join-Path $repoRoot "user_data\backtest_results"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

$composeArgs = @(
    "-f", $composeFile,
    "run", "--rm", "--no-deps", "freqtrade-dryrun",
    "backtesting",
    "--config", "/freqtrade/config/base.spot.json",
    "--config", "/freqtrade/config/dryrun.json",
    "--strategy", $Strategy,
    "--timerange", $Timerange,
    "--timeframe-detail", $TimeframeDetail,
    "--backtest-directory", "/freqtrade/user_data/backtest_results",
    "--enable-protections",
    "--breakdown", "day", "month",
    "--export", "trades",
    "--cache", "none"
)

if ($Notes) {
    $composeArgs += @("--notes", $Notes)
}

& docker compose @composeArgs 2>&1 | Tee-Object -FilePath $stdoutPath

& $pythonExe (Join-Path $repoRoot "scripts\render_backtest_report.py") `
    --stdout-path $stdoutPath `
    --artifact-dir $artifactDir `
    --output-path $markdownPath `
    --strategy $Strategy `
    --timerange $Timerange `
    --timeframe-detail $TimeframeDetail `
    --notes $Notes

Write-Host "Backtest log: $stdoutPath"
Write-Host "Backtest report: $markdownPath"

