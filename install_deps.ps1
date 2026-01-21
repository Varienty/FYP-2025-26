# Installs Python dependencies from requirements.txt into the active venv
# Usage:
#   .\.venv\Scripts\Activate.ps1
#   .\install_deps.ps1

$ErrorActionPreference = "Stop"

# Ensure we're in the repo root (where requirements.txt exists)
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $repoRoot

if (-not (Test-Path "$repoRoot\requirements.txt")) {
    Write-Error "requirements.txt not found at $repoRoot. Run this from the project root."
}

# Ensure pip points to the venv
try {
    $pipVersion = pip --version
    Write-Host "Using pip: $pipVersion"
} catch {
    Write-Error "pip is not available. Activate your virtual environment first: .\\.venv\\Scripts\\Activate.ps1"
}

Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Cyan
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Dependency installation complete." -ForegroundColor Green

Pop-Location
