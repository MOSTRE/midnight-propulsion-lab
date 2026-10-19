# Packaging and execution audit

Audit date: 2026-10-19.

## Checks completed in the current packaging pass

| Check | Result | Notes |
|---|---|---|
| Automated tests | PASS — 11 tests | `python -m pytest -q` |
| Python compilation | PASS | `python -m compileall -q src tests app` |
| Editable package build | PASS with local build settings | `python -m pip install -e . --no-build-isolation --no-deps` |
| Baseline and uncertainty screen | PASS | 2,000 samples, seed `20261019` |
| Core figures | PASS | Regenerated from the current result files; mass-margin plot now uses separate architecture panels |
| Deterministic trajectory benchmark | PASS under stated surrogate assumptions | 365-day circular-coplanar, Sun-gravity-only benchmark |
| Trajectory figures | PASS | Regenerated from the trajectory JSON output |
| Local Markdown links | PASS | No broken relative links found in the Markdown files during this audit |
| Streamlit source compilation | PASS | Included in `compileall` |

## Checks not completed in this environment

- A normal isolated `pip install -e .` could not download build requirements because this execution environment had no access to the package index. The editable package build succeeded with `--no-build-isolation --no-deps`; on a connected computer, use the normal install command in the README.
- Streamlit is not installed in this environment, so an actual dashboard startup test was not possible. It is declared as a runtime dependency and will be installed by `pip install -e ".[dev]"` on a connected machine.
- A fresh invocation of the three-start, 40-evaluation optimizer diagnostic exceeded the available execution window. The repository retains its previous recorded diagnostic in `results/trajectory_multistart.json`; its recorded runs all passed the deliberately loose terminal gates but none met the optimizer convergence criterion. Do not interpret those incomplete iterates as optimal solutions.

## Recorded numerical results

- Screening counts: NEP `1288/2000`, NTP `321/2000`, no feasible architecture `391/2000`, chemical `0/2000` selected under the configured input distributions.
- Baseline NEP screen: `+3283.7 kg` mass margin, `30.59 N` idealized thrust, approximately `152.0 m²` estimated radiator area.
- Separate trajectory surrogate: approximately `4031.6 kg` propellant, `6119.7 m` final position residual, and `0.01226 m/s` final velocity residual. The position and velocity gates are `500,000 km` and `500 m/s`, respectively, and are deliberately loose.

All results are model-derived. The trajectory benchmark is not an operational mission analysis, and the uncertainty counts are not real-world probabilities.
