$ErrorActionPreference = "Stop"

Write-Host "Running the experimental circular-orbit Earth-to-Mars NEP benchmark..." -ForegroundColor Cyan
python -m midnight_propulsion_lab.cli trajectory

Write-Host "Generating trajectory figures..." -ForegroundColor Cyan
python -m midnight_propulsion_lab.cli trajectory-figures

Write-Host "Trajectory run complete. This is a low-fidelity surrogate, not a validated flight trajectory." -ForegroundColor Yellow
Write-Host "The multi-start optimization diagnostic is slower; see README.md and docs/trajectory_validation.md." -ForegroundColor Yellow
