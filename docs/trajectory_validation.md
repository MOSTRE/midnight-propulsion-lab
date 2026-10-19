# Reference-case validation and constraints report

The unpowered two-body propagator is checked against the analytical half-period
Earth-to-Mars Hohmann ellipse. Starting at the analytical departure state, it
returns the analytical aphelion position within 1 m and velocity within
\(10^{-5}\) m/s under the declared numerical settings. This checks the solar
gravity integration, units, state ordering, and segmented integration path; it
does not validate the low-thrust optimizer or real ephemerides.

The constrained NEP benchmark completed the configured 365-day circular-marker
rendezvous surrogate. The current deterministic run produced:

| Quantity | Result |
| --- | ---: |
| Terminal position residual | 6.12 km |
| Terminal velocity residual | 0.0123 m/s |
| Position gate | 500,000 km |
| Velocity gate | 500 m/s |
| Propellant used | 4,031.6 kg |
| Final mass | 15,968.4 kg |
| Dry-mass cutoff | 12,861.8 kg |
| Least-squares function evaluations | 65 |
| Optimizer termination | `xtol` condition satisfied |
| Terminal gates | Passed |

The trajectory `success` field records whether the configured terminal gates pass.
Optimizer termination is reported separately as `optimizer_converged`; these are not
interchangeable. The least-squares method finds a local solution and does not
establish global optimality or robustness to alternate initial guesses.

## Numerical issue found and repaired

The initial implementation integrated across piecewise-constant control changes
inside one adaptive solve. That meant a Runge-Kutta step could evaluate the
right-hand side on both sides of a control discontinuity. Frozen-control reruns
under tighter tolerances differed by roughly 6,440 km in final position.

The propagator now integrates each control arc separately and lands exactly on
each segment boundary. A terminal event stops integration at the dry-mass
constraint. The controls and the segment boundaries are checked in automated
tests.

With the optimized control vector frozen, changing propagation tolerances from
`rtol=1e-9, atol=1e-2` to `rtol=1e-11, atol=1e-4` changed final position by
0.0084 m, final velocity by approximately \(9.13\times10^{-10}\) m/s, and final
mass by approximately \(1.64\times10^{-11}\) kg. This is evidence of integration
stability for this frozen control history, not evidence that the optimizer found
a globally optimal solution or that the model represents an operational mission.

## Limits that remain

The position gate is 500,000 km and the velocity gate is 500 m/s. They are loose
screening thresholds, not Mars capture, rendezvous navigation, or mission design
requirements. The benchmark omits planetary gravity, real ephemerides, Earth
escape, Mars capture, launch energy, and operational restrictions. Multiple-start
and global-optimization analysis has not been completed.

`results/trajectory_comparison.json` is the machine-readable record.
