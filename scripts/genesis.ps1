Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

param(
    [string]$RepoUrl = "https://github.com/TUR1412/HotelManager.git",
    [string]$WorkRoot = (Get-Location).Path,
    [string]$RepoDir = "HotelManager",
    [ValidateSet("none", "push", "force-with-lease", "force")]
    [string]$PushMode = "none",
    [switch]$SelfDestruct,
    [string]$CommitMessage = "feat(GOD-MODE):  Ultimate Evolution - Quark-level UI & Arch Upgrade"
)

$patchPath = Join-Path $PSScriptRoot "genesis.patch"
if (-not (Test-Path -LiteralPath $patchPath)) {
    throw "Missing patch file: $patchPath"
}

$workRootPath = Resolve-Path -LiteralPath $WorkRoot
$repoPath = Join-Path $workRootPath $RepoDir

$didClone = $false

if (Test-Path -LiteralPath $repoPath) {
    if (-not (Test-Path -LiteralPath (Join-Path $repoPath ".git"))) {
        throw "Destination exists but is not a git repository: $repoPath"
    }
}
else {
    New-Item -ItemType Directory -Path $workRootPath -Force | Out-Null
    Write-Host "== clone ==" -ForegroundColor Cyan
    git clone $RepoUrl $repoPath
    $didClone = $true
}

Push-Location $repoPath
try {
    Write-Host "== apply patch ==" -ForegroundColor Cyan
    git apply --check $patchPath 2>$null
    if ($LASTEXITCODE -ne 0) {
        git apply -R --check $patchPath 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Patch already applied; skipping." -ForegroundColor Yellow
        }
        else {
            throw "Patch does not apply cleanly: $patchPath"
        }
    }
    else {
        git apply --whitespace=nowarn $patchPath
    }

    Write-Host "== tests ==" -ForegroundColor Cyan
    $env:PYTHONPATH = "src"
    python -m compileall -q src tests
    python -m unittest discover -s tests -v

    Write-Host "== commit ==" -ForegroundColor Cyan
    git add -A
    git diff --cached --quiet
    if ($LASTEXITCODE -eq 0) {
        Write-Host "No changes staged; skipping commit." -ForegroundColor Yellow
    }
    elseif ($LASTEXITCODE -eq 1) {
        git commit -m $CommitMessage
    }
    else {
        throw "Unexpected git exit code from diff --cached --quiet: $LASTEXITCODE"
    }

    if ($PushMode -ne "none") {
        Write-Host "== push ($PushMode) ==" -ForegroundColor Cyan
        if ($PushMode -eq "push") {
            git push
        }
        elseif ($PushMode -eq "force-with-lease") {
            git push --force-with-lease
        }
        elseif ($PushMode -eq "force") {
            git push --force
        }
        else {
            throw "Unknown PushMode: $PushMode"
        }
    }
}
finally {
    Pop-Location
}

if ($SelfDestruct) {
    if (-not $didClone) {
        throw "Refusing to self-destruct: repo was not cloned by this run ($repoPath)."
    }
    if ($PushMode -eq "none") {
        throw "SelfDestruct requires PushMode != 'none'."
    }
    Write-Host "== self-destruct ==" -ForegroundColor Cyan
    Remove-Item -Recurse -Force -LiteralPath $repoPath
}
