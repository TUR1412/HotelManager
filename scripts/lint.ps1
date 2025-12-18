Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $repoRoot
try {
    Write-Host "== ruff format (check) ==" -ForegroundColor Cyan
    python -m ruff format --check .

    Write-Host "== ruff check ==" -ForegroundColor Cyan
    python -m ruff check .
}
finally {
    Pop-Location
}
