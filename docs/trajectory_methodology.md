# Trajectory validation methodology

## Method selection

The experiment uses SciPy 1.15.2 `solve_ivp(method="DOP853")` and bounded
least-squares shooting. This was selected after checking the installed Python
3.12 environment and current documentation: SciPy provides a documented
high-order non-stiff integrator; TudatPy is distributed primarily through Conda;
and Dymos can use SciPy optimizers but its more capable Windows optimization path
has extra toolchain requirements. Adding either would not improve this explicitly
low-fidelity benchmark yet.

## Benchmark

The new benchmark is distinct from the 9 km/s screen: a planar, Sun-centered,
circular-coplanar Earth-to-Mars rendezvous surrogate with a 365-day flight time.
Earth starts at 1 au on the x axis. Mars is a prescribed circular marker at
1.523679 au, initialized at the classical Hohmann phase angle and propagated to
its 365-day target state. The state is \([x,y,v_x,v_y,m]\). Only solar gravity
is modeled:

\[
\dot{x}=v_x,\quad \dot{y}=v_y,\quad
\dot{\mathbf v}=-\mu_\odot\mathbf r/|\mathbf r|^3+
T u(\theta)\mathbf/m,\quad \dot m=-T\tau/v_e.
\]

There are eight equal-duration arcs. Each has a thrust-direction offset relative
to instantaneous velocity and throttle \(0\le\tau\le1\). Thrust is capped by
the existing 1 MWe, 60%-efficient, 4,000 s NEP case:
\(T=2\eta P/v_e=30.5915\) N. Integration uses DOP853, `rtol=1e-10`,
`atol=1e-3`, and integrates each control arc separately with a maximum step of
one eighth of an arc. Separating the solves ensures no adaptive integration step
straddles a steering/throttle discontinuity. A terminal event stops propagation
at the dry-mass cutoff. The experimental least-squares objective minimizes
normalized terminal position/velocity residuals plus a small throttle-use
regularizer; it is a local feasibility search, not a global optimal-control proof.
The record separates passing the terminal gates from convergence of the optimizer.
A deterministic multi-start diagnostic can perturb the baseline initial controls;
its run count, seed, per-start evaluation budget, terminal-gate outcomes, and
optimizer status are preserved separately. Incomplete runs must not be ranked by
propellant use as if they were converged optima.

The arrival gates are 500,000 km and 500 m/s. They are intentionally loose
screening gates, not Mars capture or navigation requirements.

## Explicit omissions

No planetary gravity, ephemerides, Earth escape, Mars capture, launch C3,
eclipse, duty-cycle, power degradation, attitude constraints, reliability, or
operational navigation is modeled. The benchmark must not be interpreted as a
flight trajectory.

SciPy is BSD-3-Clause licensed. TudatPy (BSD-3-Clause) and GMAT (Apache-2.0)
were viable open-source alternatives, but neither was installed for this milestone.
