Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $repoRoot
try {
    $env:PYTHONPATH = "src"

    Write-Host "== compileall ==" -ForegroundColor Cyan
    python -m compileall -q src tests

    Write-Host "== unittest ==" -ForegroundColor Cyan
    python -m unittest discover -s tests -v
}
finally {
    Pop-Location
}

