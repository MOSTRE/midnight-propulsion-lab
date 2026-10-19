# Continuation report — 2026-10-19

This update continued work from the uploaded project archive. It did not replace
the existing architecture screen or overwrite its Monte Carlo output.

## What changed

- Reworked the NEP propagator to integrate each piecewise-constant control arc
  separately. Adaptive integration no longer takes steps across steering/throttle
  discontinuities.
- Added a terminal dry-mass event so propagation stops at propellant depletion.
- Added validation for benchmark settings and control bounds, plus tests for
  strictly increasing propagation time and exact segment-boundary inclusion.
- Split terminal-gate success from least-squares optimizer convergence in the
  recorded trajectory output. The dashboard now displays both statuses.
- Relaxed the least-squares termination tolerances to a documented `1e-8` so the
  baseline case stops on a numerical termination condition rather than exhausting
  its function-evaluation budget.
- Added a deterministic, seeded multi-start diagnostic and a plot showing how
  final propellant use depends on the initial control guess.

## Reproduced results

The existing 2,000-sample screen reproduced with seed `20261019`: NEP selected in
1,288 samples, NTP in 321, and no architecture feasible in 391. These are model
outputs under the declared synthetic input distributions, not empirical mission
probabilities.

The single-start NEP trajectory surrogate passed its configured terminal gates
in 365 days, with a 6.12 km position residual and 0.0123 m/s velocity residual.
It used 4,031.6 kg of propellant in the separate trajectory benchmark. Its
least-squares optimizer reported the `xtol` termination condition after 65
function evaluations.

With the single-start controls frozen, tightening propagation tolerances changed
final position by 0.0084 m, velocity by about `9.13e-10 m/s`, and mass by about
`1.64e-11 kg`. This supports integrator stability for those controls, not global
optimality or mission fidelity.

The three-start sensitivity diagnostic used seed `20261019` and 40 function
evaluations per start. All three final iterates passed the deliberately loose
terminal gates; none met the optimizer's convergence criterion within that
budget. Their propellant use ranged from 3,936.6 to 4,440.9 kg. Do not interpret
that range as a range of optima: it reflects incomplete local-search iterates.

## Checks

- `python -m pytest -q`: 11 passed.
- `python -m compileall -q src tests app`: passed.
- Baseline screen, figure generation, single-start trajectory, and multi-start
  diagnostic commands completed.
- Editable package installation succeeded with `python -m pip install -e .
  --no-build-isolation --no-deps`. A normal isolated install could not fetch build
  dependencies because this runtime cannot reach package indexes. Streamlit is
  not installed in this runtime, so dashboard startup was not re-tested here; the
  dashboard source compiles, but a runtime smoke test remains for the normal
  project environment.

## What remains

The benchmark still has only Sun gravity, circular planetary markers, a 500,000 km
position gate, and a 500 m/s velocity gate. It omits real ephemerides, Earth
escape, Mars capture, and operational mission constraints. Only NEP is currently
propagated, so this experiment does not rank chemical, NTP, and NEP on equivalent
trajectories.

The next serious step is to improve constrained-optimizer robustness, then validate
against a published trajectory/reference case or a second independent tool before
using this model to make architecture-selection claims.
