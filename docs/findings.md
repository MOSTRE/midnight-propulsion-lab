# Findings

## Baseline screen

For the generic 20,000 kg / 2,000 kg payload / 9 km/s equivalent-delta-v / 365-day scenario, the mass-budget screen returns:

- Chemical: infeasible by 55.42 t of initial-mass budget.
- Nuclear thermal (NTP): infeasible by 1.72 t.
- Nuclear electric (NEP): feasible in this screen with 3.28 t of mass margin.

The NEP baseline assumptions produce 30.59 N of idealized thrust and an estimated radiator area of approximately 152 m². These are model-derived results from declared assumptions, not predictions for a flight vehicle. NEP duration screening uses a constant-thrust average-acceleration proxy rather than an optimized trajectory.

## Joint uncertainty stress test

With seed `20261019` and 2,000 synthetic samples, NEP is selected in 1,288 cases, NTP in 321, and no architecture is feasible in 391. Chemical propulsion is selected in zero cases under these inputs and this selection rule. The input distributions are stress-test assumptions, not empirically calibrated probabilities.

## Separate trajectory benchmark

The circular-coplanar, Sun-centered Earth-to-Mars surrogate finds a local NEP control history meeting its deliberately loose arrival gates after a 365-day propagation. It uses approximately 4.03 t of propellant, with 6.12 km position residual and 0.0123 m/s velocity residual. The model omits real ephemerides, planetary gravity, Earth escape, Mars capture, and operational constraints. Multi-start attempts did not converge within their 40-evaluation budgets, so there is no robust optimality claim.

## Interpretation

The current contribution is a reproducible screening, uncertainty, and exploratory trajectory workflow. The results do not establish a new propulsion invention, a novel physical principle, patentability, or real mission feasibility. A validated trajectory benchmark and more robust optimization are the next research priorities.

Reproduce the baseline results with `python -m midnight_propulsion_lab.cli run --samples 2000 --seed 20261019`. Machine-readable outputs are under `results/`.
