# Changelog

## 0.1.0 — 2026-10-19

- Initial literature screen, low-fidelity screening package, seeded uncertainty
  experiment, dashboard, figures, audit notes, and tests.
- Repaired a high-delta-v tank/propellant closure divergence discovered by figure QA.
- Added an experimental constrained NEP trajectory benchmark, analytical two-body
  reference check, propellant-depletion check, terminal-residual figure, and
  numerical-tolerance record.
- Corrected the NEP trajectory integrator to stop exactly at steering/throttle
  segment boundaries and added a terminal dry-mass event. Added optimizer-convergence
  metadata separately from terminal-gate status and expanded trajectory tests.
- Added deterministic multi-start trajectory diagnostics to expose local-solver
  initialization sensitivity, with explicit reporting when the evaluation budget
  is exhausted before optimizer convergence.
- Expanded the README with plain-language interpretation, actual recorded outputs,
  direct figure previews, and explicit limitations.
- Added a Windows-friendly publishing guide and scripts for reproducing the core
  screening analysis and the separate trajectory benchmark.
- Added a GitHub Actions workflow for tests, compilation, and a small reproduction run.
- Reworked the mass-margin figure into separate architecture panels so large
  chemical/NTP mass shortfalls do not hide the NEP crossover.
