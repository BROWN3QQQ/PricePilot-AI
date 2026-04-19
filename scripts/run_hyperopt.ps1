param(
    [string]$Timerange = "20240101-",
    [string]$Strategy = "BinanceSpotLowFrequencyStrategy",
    [int]$Epochs = 200,
    [int]$EarlyStop = 50,
    [string[]]$Spaces = @("buy", "sell", "roi", "stoploss", "protection"),
    [string]$LossFunction = "MultiMetricHyperOptLoss"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra\docker-compose.yml"
$reportDir = Join-Path $repoRoot "reports\hyperopt"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$stdoutPath = Join-Path $reportDir "$timestamp-$Strategy-hyperopt.log"
$markdownPath = Join-Path $reportDir "$timestamp-$Strategy-hyperopt.md"
$artifactDir = Join-Path $repoRoot "user_data\hyperopt_results"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

$composeArgs = @(
    "-f", $composeFile,
    "run", "--rm", "--no-deps", "freqtrade-dryrun",
    "hyperopt",
    "--config", "/freqtrade/config/base.spot.json",
    "--config", "/freqtrade/config/dryrun.json",
    "--strategy", $Strategy,
    "--timerange", $Timerange,
    "--hyperopt-loss", $LossFunction,
    "--epochs", $Epochs.ToString(),
    "--early-stop", $EarlyStop.ToString(),
    "--spaces"
)

$composeArgs += $Spaces
$composeArgs += @(
    "--analyze-per-epoch",
    "--print-json",
    "--no-color"
)

& docker compose @composeArgs 2>&1 | Tee-Object -FilePath $stdoutPath

& $pythonExe (Join-Path $repoRoot "scripts\render_hyperopt_report.py") `
    --stdout-path $stdoutPath `
    --artifact-dir $artifactDir `
    --output-path $markdownPath `
    --strategy $Strategy `
    --timerange $Timerange `
    --loss-function $LossFunction `
    --epochs $Epochs `
    --spaces ($Spaces -join ",")

Write-Host "Hyperopt log: $stdoutPath"
Write-Host "Hyperopt report: $markdownPath"

