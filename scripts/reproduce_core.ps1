$ErrorActionPreference = "Stop"

Write-Host "Installing the project and test dependency..." -ForegroundColor Cyan
python -m pip install -e ".[dev]"

Write-Host "Running automated tests..." -ForegroundColor Cyan
python -m pytest -q

Write-Host "Compiling Python source..." -ForegroundColor Cyan
python -m compileall -q src tests app

Write-Host "Reproducing the baseline and 2,000-sample uncertainty screen..." -ForegroundColor Cyan
python -m midnight_propulsion_lab.cli run --samples 2000 --seed 20261019

Write-Host "Generating the plots..." -ForegroundColor Cyan
python -m midnight_propulsion_lab.cli figures

Write-Host "Core research run complete. The separate trajectory experiment is in scripts/reproduce_trajectory.ps1." -ForegroundColor Green
