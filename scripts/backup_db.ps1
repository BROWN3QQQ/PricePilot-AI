param()

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$backupRoot = Join-Path $repoRoot "user_data\backups"
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$target = Join-Path $backupRoot $timestamp
$sources = @(
    (Join-Path $repoRoot "user_data\tradesv3.dryrun.sqlite"),
    (Join-Path $repoRoot "user_data\tradesv3.live.sqlite")
)

if (-not (Test-Path $backupRoot)) {
    New-Item -ItemType Directory -Path $backupRoot | Out-Null
}

New-Item -ItemType Directory -Path $target | Out-Null

foreach ($source in $sources) {
    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $target
    }
}

Copy-Item -Path (Join-Path $repoRoot "config\*.json") -Destination $target

Write-Host "Backup written to $target"

