# Research log

- 2026-10-19: Created the Stage 0 source protocol, search log, initial annotated
  bibliography, and limited prior-art matrix.
- 2026-10-19: Chose uncertainty-aware architecture-screening reproducibility as
  the primary direction after finding established work on NEP mass/trajectory
  coupling, radiators, and hybrid concepts.
- 2026-10-19: Implemented a mass, thrust, and radiator screen with a seeded
  Monte Carlo stress test.
- 2026-10-19: Visual inspection exposed tank/propellant-loop divergence at high
  delta-v. Replaced the iterative closure with its exact finite-solution test and
  regenerated results.
- 2026-10-19: Audited the screening code and implemented a separate planar,
  Sun-centered bounded-thrust trajectory benchmark. Verified an unpowered Hohmann
  propagation against its analytical two-body endpoint and recorded the low-thrust
  solver/tolerance limitations. No original Monte Carlo result was overwritten.
- 2026-10-19: Numerical QA found that the first trajectory implementation allowed
  adaptive integration steps to straddle piecewise-constant control boundaries.
  Split propagation at every control boundary and added a terminal dry-mass event.
  The frozen-control tolerance discrepancy fell from roughly 6,440 km to 0.0084 m
  in final position. Added checks for monotonic time, boundary inclusion, and
  throttle bounds; the suite now reports 11 passing tests. The optimizer's gate
  result and convergence status are now recorded separately.
- 2026-10-19: Added a seeded three-start shooting diagnostic. All three end states
  passed the deliberately loose terminal gates, but none met optimizer convergence
  within 40 function evaluations. The incomplete iterates used 3.94–4.44 t of
  propellant; this is treated as initialization/budget sensitivity, not as a valid
  optimum range. Added a diagnostic figure and documented the remaining solver work.
