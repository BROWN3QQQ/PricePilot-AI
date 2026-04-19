param(
    [string]$Timerange = "20240101-",
    [string[]]$Timeframes = @("15m", "1h", "4h"),
    [string[]]$Pairs = @("BTC/USDT", "ETH/USDT", "SOL/USDT", "XRP/USDT", "ADA/USDT")
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra\docker-compose.yml"

$composeArgs = @(
    "-f", $composeFile,
    "run", "--rm", "--no-deps", "freqtrade-dryrun",
    "download-data",
    "--config", "/freqtrade/config/base.spot.json",
    "--config", "/freqtrade/config/dryrun.json",
    "--timerange", $Timerange,
    "--timeframes"
)

$composeArgs += $Timeframes
$composeArgs += "--pairs"
$composeArgs += $Pairs

& docker compose @composeArgs
