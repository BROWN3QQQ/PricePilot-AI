param()

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$composeFile = Join-Path $repoRoot "infra\docker-compose.yml"
$requiredDirs = @(
    (Join-Path $repoRoot "user_data\data"),
    (Join-Path $repoRoot "user_data\logs"),
    (Join-Path $repoRoot "user_data\backups"),
    (Join-Path $repoRoot "user_data\backtest_results"),
    (Join-Path $repoRoot "user_data\hyperopt_results"),
    (Join-Path $repoRoot "reports\backtests"),
    (Join-Path $repoRoot "reports\hyperopt"),
    (Join-Path $repoRoot "reports\daily")
)

foreach ($path in $requiredDirs) {
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path | Out-Null
    }
}

docker version | Out-Null
docker compose -f $composeFile --profile dryrun pull

Write-Host "Bootstrap complete."
Write-Host "Next steps:"
Write-Host "  1. Review config files in .\config"
Write-Host "  2. Run .\scripts\download_data.ps1"
Write-Host "  3. Run .\scripts\validate_strategy.ps1"
Write-Host "  4. Run .\scripts\run_dry.ps1"
