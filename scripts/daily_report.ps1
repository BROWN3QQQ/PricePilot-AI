param(
    [ValidateSet("dryrun", "live")]
    [string]$Mode = "dryrun",
    [int]$Days = 1,
    [string]$Date = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$reportDir = Join-Path $repoRoot "reports\daily"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$dbPath = if ($Mode -eq "live") {
    Join-Path $repoRoot "user_data\tradesv3.live.sqlite"
} else {
    Join-Path $repoRoot "user_data\tradesv3.dryrun.sqlite"
}

if (-not (Test-Path $reportDir)) {
    New-Item -ItemType Directory -Path $reportDir | Out-Null
}

$pythonArgs = @(
    (Join-Path $repoRoot "scripts\render_daily_report.py"),
    "--db-path", $dbPath,
    "--output-dir", $reportDir,
    "--mode", $Mode,
    "--days", $Days.ToString()
)

if ($Date) {
    $pythonArgs += @("--date", $Date)
}

& $pythonExe @pythonArgs
