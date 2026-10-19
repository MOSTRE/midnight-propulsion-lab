# Registered initial hypothesis — 2026-10-19

For the generic equivalent-delta-v mission family in `configs/baseline.yaml`, a
point-estimate architecture ranking will be less stable than it appears once NEP
power-system specific mass, radiator areal density, thruster efficiency, launch
mass, delta-v, and allowed duration vary jointly. The metric is the share of
screening samples for which an architecture is feasible and has the largest mass
margin. The baseline is the nominal mass-margin ranking. The hypothesis is
supported only if the nominal winner has a materially lower selection share under
the declared stress-test distributions; it is refuted if its ranking is stable.

This does not assert that robust optimization is new. It tests whether a compact,
auditable screen shows a meaningful reversal worth validating with trajectories.
