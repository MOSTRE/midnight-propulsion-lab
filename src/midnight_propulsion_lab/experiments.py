"""Repeatable baseline, sweep, and Monte-Carlo experiments."""
from __future__ import annotations

import csv
import json
from dataclasses import asdict, replace
from pathlib import Path

import numpy as np

from .mission import BASELINES, Architecture, Scenario, evaluate
from .trajectory import (TrajectoryBenchmark, default_control_guess, propulsion_mass_state,
                         propagate, solve_nep_benchmark)


def baseline_rows(scenario: Scenario = Scenario()) -> list[dict]:
    return [evaluate(scenario, a).record() for a in BASELINES.values()]


def crossover_sweep() -> list[dict]:
    rows = []
    for dv in np.arange(4_000, 20_001, 500):
        scenario = Scenario(delta_v_m_s=float(dv))
        for name, arch in BASELINES.items():
            row = evaluate(scenario, arch).record()
            row["delta_v_m_s"] = float(dv)
            rows.append(row)
    return rows


def monte_carlo(n: int = 2_000, seed: int = 20261019) -> list[dict]:
    """Joint uncertainty screen; distributions are scenario assumptions, not measurements."""
    rng = np.random.default_rng(seed)
    rows = []
    for index in range(n):
        scenario = Scenario(delta_v_m_s=float(rng.uniform(6_000, 14_000)),
                            duration_days=float(rng.uniform(180, 600)),
                            initial_mass_kg=float(rng.uniform(16_000, 28_000)))
        # Lognormal positive mass multipliers, deliberately broad for a screening stress test.
        alpha = float(np.exp(rng.normal(np.log(8.0), 0.35)))
        radiator_density = float(np.exp(rng.normal(np.log(6.0), 0.30)))
        efficiency = float(np.clip(rng.normal(0.60, 0.06), 0.35, 0.8))
        arch = replace(BASELINES["nep"], power_specific_mass_kg_kw=alpha,
                       radiator_areal_density_kg_m2=radiator_density, efficiency=efficiency)
        results = {k: evaluate(scenario, a) for k, a in BASELINES.items() if k != "nep"}
        results["nep"] = evaluate(scenario, arch)
        feasible = [r for r in results.values() if r.feasible]
        best = max(feasible, key=lambda r: r.payload_margin_kg).architecture if feasible else "none"
        for name, result in results.items():
            row = result.record() | {"sample": index, "selected": name == best, "best": best,
                                     "delta_v_m_s": scenario.delta_v_m_s, "duration_days": scenario.duration_days,
                                     "initial_mass_kg": scenario.initial_mass_kg, "nep_alpha_kg_kw": alpha,
                                     "radiator_density_kg_m2": radiator_density, "nep_efficiency": efficiency}
            rows.append(row)
    return rows


def write_rows(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader(); writer.writerows(rows)


def run_all(root: Path, n: int = 2_000, seed: int = 20261019) -> dict:
    root.mkdir(parents=True, exist_ok=True)
    base, sweep, mc = baseline_rows(), crossover_sweep(), monte_carlo(n, seed)
    write_rows(base, root / "baseline.csv"); write_rows(sweep, root / "crossover_sweep.csv"); write_rows(mc, root / "monte_carlo.csv")
    summary = {"seed": seed, "samples": n, "baseline": base,
               "selection_counts": {name: sum(r["best"] == name for r in mc[::3]) for name in ("chemical", "ntp", "nep", "none")}}
    (root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def run_trajectory(root: Path) -> dict:
    """Run the separate deterministic trajectory-validation benchmark."""
    root.mkdir(parents=True, exist_ok=True)
    scenario, architecture, benchmark = Scenario(), BASELINES["nep"], TrajectoryBenchmark()
    screen = evaluate(scenario, architecture)
    trajectory = solve_nep_benchmark(scenario, architecture)
    # Reintegrate the frozen control with a tighter tolerance: this checks
    # propagation convergence without claiming optimizer-global convergence.
    initial_mass, dry_mass, thrust, mdot = propulsion_mass_state(scenario, architecture)
    from .trajectory import circular_state, EARTH_ORBIT_RADIUS_M
    controls = np.asarray(trajectory.controls)
    loose = propagate(replace(benchmark, rtol=1e-9, atol=1e-2), circular_state(EARTH_ORBIT_RADIUS_M, 0), initial_mass,
                      dry_mass, thrust, mdot, controls[:benchmark.segments], controls[benchmark.segments:])
    tight = propagate(replace(benchmark, rtol=1e-11, atol=1e-4), circular_state(EARTH_ORBIT_RADIUS_M, 0), initial_mass,
                      dry_mass, thrust, mdot, controls[:benchmark.segments], controls[benchmark.segments:])
    delta = loose.y[:4, -1] - tight.y[:4, -1]
    convergence = {"frozen_control_final_position_difference_m": float(np.linalg.norm(delta[:2])),
                   "frozen_control_final_velocity_difference_m_s": float(np.linalg.norm(delta[2:])),
                   "frozen_control_final_mass_difference_kg": float(abs(loose.y[4, -1] - tight.y[4, -1]))}
    report = {"benchmark": "circular-coplanar Sun-centered Earth-to-Mars surrogate",
              "screening_proxy": screen.record(), "trajectory": trajectory.record(),
              "propagation_convergence": convergence,
              "interpretation": "The trajectory result is an experimental bounded-control feasibility search, not a full ephemeris or planetary-capture mission."}
    (root / "trajectory_comparison.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

def run_trajectory_multistart(root: Path, starts: int = 3, seed: int = 20261019,
                              max_nfev: int = 40) -> dict:
    """Test sensitivity of the local NEP shooting search to initial controls.

    This is a small, reproducible local-optimizer diagnostic, not a global search.
    Alternative starts are perturbed around a physically motivated low-duty seed
    so they remain distinct without deliberately beginning at propellant-depleting
    control histories.
    """
    if starts < 1:
        raise ValueError("starts must be at least 1")
    root.mkdir(parents=True, exist_ok=True)
    scenario, architecture = Scenario(), BASELINES["nep"]
    benchmark = TrajectoryBenchmark()
    n = benchmark.segments
    baseline_guess = default_control_guess(n)
    rng = np.random.default_rng(seed)
    guesses = [baseline_guess]
    for _ in range(1, starts):
        guess = baseline_guess.copy()
        guess[:n] = np.clip(guess[:n] + rng.normal(0.0, 0.45, n), -np.pi + 1e-6, np.pi - 1e-6)
        guess[n:] = np.clip(guess[n:] + rng.normal(0.0, 0.025, n), 0.0, 0.70)
        guesses.append(guess)

    runs: list[dict] = []
    for index, guess in enumerate(guesses):
        try:
            result = solve_nep_benchmark(scenario, architecture, benchmark,
                                         max_nfev=max_nfev, initial_controls=guess)
            runs.append({"start_index": index, "error": None, "result": result.record()})
        except (RuntimeError, ValueError) as exc:
            runs.append({"start_index": index, "error": f"{type(exc).__name__}: {exc}", "result": None})

    completed = [r for r in runs if r["result"] is not None]
    terminal_passes = [r for r in completed if r["result"]["success"]]
    converged = [r for r in completed if r["result"]["optimizer_converged"]]
    qualified = [r for r in completed if r["result"]["success"] and r["result"]["optimizer_converged"]]
    best = min(qualified, key=lambda r: r["result"]["propellant_used_kg"]) if qualified else None
    propellant_values = [r["result"]["propellant_used_kg"] for r in qualified]
    gate_pass_propellant_values = [r["result"]["propellant_used_kg"] for r in terminal_passes]
    best_gate_pass = min(terminal_passes, key=lambda r: r["result"]["propellant_used_kg"]) if terminal_passes else None
    report = {
        "benchmark": "circular-coplanar Sun-centered Earth-to-Mars surrogate",
        "seed": seed,
        "starts_requested": starts,
        "max_nfev_per_start": max_nfev,
        "completed_count": len(completed),
        "terminal_gate_pass_count": len(terminal_passes),
        "optimizer_converged_count": len(converged),
        "gate_pass_and_converged_count": len(qualified),
        "gate_pass_propellant_range_kg": ([min(gate_pass_propellant_values), max(gate_pass_propellant_values)]
                                           if gate_pass_propellant_values else None),
        "best_gate_pass_start_index": best_gate_pass["start_index"] if best_gate_pass else None,
        "qualified_propellant_range_kg": ([min(propellant_values), max(propellant_values)]
                                           if propellant_values else None),
        "best_qualified_start_index": best["start_index"] if best else None,
        "best_qualified_result": best["result"] if best else None,
        "runs": runs,
        "interpretation": (
            "This deterministic multi-start check probes sensitivity to a small set of local initial guesses. "
            "It is not a global-optimality proof, a probability estimate, or an operational mission result."
        ),
    }
    (root / "trajectory_multistart.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report

