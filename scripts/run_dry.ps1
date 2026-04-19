param()

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra\docker-compose.yml"

docker compose -f $composeFile --profile dryrun up -d freqtrade-dryrun

Write-Host "Dry-run bot started."
Write-Host "UI/API: http://127.0.0.1:8080"

