param()

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra\docker-compose.yml"
$privateConfig = Join-Path $repoRoot "config\private.live.json"

if (-not (Test-Path $privateConfig)) {
    throw "Missing config\private.live.json. Copy config\private.live.template.json first."
}

docker compose -f $composeFile --profile live up -d freqtrade-live

Write-Host "Live bot started."
Write-Host "UI/API: http://127.0.0.1:8081"

