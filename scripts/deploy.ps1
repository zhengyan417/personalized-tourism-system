param(
    [string]$PythonExe = "python",
    [string]$NpmExe = "npm",
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$BuildFrontend,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"

function Invoke-Step {
    param(
        [string]$Title,
        [ScriptBlock]$Action
    )
    Write-Host "`n=== $Title ===" -ForegroundColor Cyan
    & $Action
}

$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "frontend"
$venvDir = Join-Path $root ".venv"
$venvPython = if ($IsWindows) { Join-Path $venvDir "Scripts\python.exe" } else { Join-Path $venvDir "bin/python" }

if (-not (Test-Path $backend)) {
    throw "Backend directory not found: $backend"
}
if (-not (Test-Path $frontend)) {
    throw "Frontend directory not found: $frontend"
}

if (-not $SkipBackend) {
    Invoke-Step "Creating Python virtual environment" {
        if (-not (Test-Path $venvPython)) {
            & $PythonExe -m venv $venvDir
        } else {
            Write-Host "Virtual environment already exists at $venvDir"
        }
    }

    Invoke-Step "Installing backend dependencies" {
        & $venvPython -m pip install --upgrade pip
        & $venvPython -m pip install -r (Join-Path $backend "requirements.txt")
    }
}

if (-not $SkipFrontend) {
    Invoke-Step "Installing frontend packages" {
        Push-Location $frontend
        try {
            & $NpmExe install
        } finally {
            Pop-Location
        }
    }
}

if ($BuildFrontend -and -not $SkipFrontend) {
    Invoke-Step "Building frontend" {
        Push-Location $frontend
        try {
            & $NpmExe run build
        } finally {
            Pop-Location
        }
    }
}

Write-Host "`nDeployment preparation complete." -ForegroundColor Green
Write-Host "Backend venv: $venvDir"
Write-Host "To start backend:"
Write-Host "  $venvPython backend/app.py" -ForegroundColor DarkGray
Write-Host "To serve frontend in dev mode:"
Write-Host "  cd $frontend && npm run serve" -ForegroundColor DarkGray
