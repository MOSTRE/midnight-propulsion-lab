# Screening versus trajectory-constrained comparison

For matched NEP hardware assumptions, both models accept the nominal case, but
they mean different things. The screening model says only that its mass budget
and average-acceleration inequality are satisfied. The trajectory experiment
finds one bounded, piecewise-controlled solution meeting the configured surrogate
arrival gates in 365 days.

The screening mass closure allocated 3,569.0 kg of propellant for its 9 km/s
equivalent-delta-v calculation and left 3,283.7 kg launch margin. The separate
trajectory benchmark starts at 20,000 kg and its found solution uses 4,031.6 kg
of propellant. This is not an apples-to-apples performance improvement; it is a
result of the trajectory benchmark's explicitly different mass-capacity rule.
No architecture ranking or Monte Carlo result is inferred from this single NEP
trajectory run.

The current optimizer satisfied the benchmark's deliberately loose arrival gates
with a 6.12 km position residual and a 0.0123 m/s velocity residual. The optimizer
reported its `xtol` termination condition. With the control vector frozen, a
propagation-tolerance comparison changed the final position by 0.0084 m. This
supports numerical stability of the propagated trajectory for those controls;
it does not establish global optimality, realistic Mars arrival conditions, or
mission feasibility. The 500,000 km and 500 m/s gates are not capture or
navigation requirements.

The important methodological result is that explicit integration at control
boundaries removed a large tolerance-dependent trajectory discrepancy observed
in the earlier implementation. The screening model remains a separate low-fidelity
architecture filter. A published ephemeris-based reference and multiple-start
optimization are still needed before using the trajectory model to rank missions.

Machine-readable details are in `results/trajectory_comparison.json`.
