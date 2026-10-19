# Generated results

The CSV and JSON files in this folder are produced by the repository's CLI. They are committed so readers can inspect the last recorded outputs without installing the software first.

To regenerate the architecture screen with the reference seed:

```powershell
python -m midnight_propulsion_lab.cli run --samples 2000 --seed 20261019
```

To regenerate the screen and uncertainty figures:

```powershell
python -m midnight_propulsion_lab.cli figures
```

To regenerate the separate trajectory benchmark:

```powershell
python -m midnight_propulsion_lab.cli trajectory
python -m midnight_propulsion_lab.cli trajectory-figures
```

`trajectory_multistart.json` is the recorded result of an expensive local-optimizer diagnostic. Its current three runs pass the configured loose terminal gates, but none converges within its 40-evaluation budget. Its propellant numbers are not converged optima. Rerun it explicitly with the `trajectory-multistart` command; it may take several minutes.

Always read `docs/limitations.md` and `docs/trajectory_validation.md` before interpreting these outputs. The uncertainty distributions are synthetic stress-test inputs, not empirical probability distributions.
