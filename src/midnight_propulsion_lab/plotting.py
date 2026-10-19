from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


PALETTE = {"chemical": "#d6a85d", "ntp": "#65c7d0", "nep": "#f4f0e6"}

def _style():
    plt.style.use("dark_background")

def make_figures(results: Path, figures: Path) -> None:
    figures.mkdir(parents=True, exist_ok=True); _style()
    with (results / "crossover_sweep.csv").open(encoding="utf-8") as f: rows = list(csv.DictReader(f))
    # Different architectures span very different mass-margin magnitudes. A single
    # shared y-axis makes the NEP crossover unreadable, so each panel gets its own
    # y-scale and the title explicitly warns readers not to compare bar heights.
    fig, axes = plt.subplots(3, 1, figsize=(9.5, 9), sharex=True, constrained_layout=True)
    for ax, arch in zip(axes, PALETTE, strict=True):
        r = [x for x in rows if x["architecture"] == arch]
        x = [float(item["delta_v_m_s"]) / 1000 for item in r]
        y = [float(item["payload_margin_kg"]) / 1000 for item in r]
        ax.plot(x, y, label=arch.upper(), color=PALETTE[arch], lw=2.4)
        ax.axhline(0, color="#8b8f90", lw=0.9, linestyle="--")
        ax.axvline(9, color="#8b8f90", lw=0.8, linestyle=":", alpha=0.8)
        ax.set_ylabel("Mass margin [t]")
        ax.set_title(arch.upper(), loc="left", fontsize=11, pad=4)
        ax.grid(alpha=.18)
        ax.legend(loc="best", framealpha=.35)
    axes[-1].set_xlabel("Required equivalent Δv [km/s]")
    fig.suptitle("Mass-budget screen by architecture", fontsize=16)
    fig.savefig(figures / "crossover_mass_margin.svg")
    fig.savefig(figures / "crossover_mass_margin.png", dpi=180)
    plt.close(fig)

    with (results / "monte_carlo.csv").open(encoding="utf-8") as f: mc = list(csv.DictReader(f))
    sample_records: dict[str, dict[str, str]] = {}
    for row in mc:
        sample_records.setdefault(row["sample"], row)
    samples = list(sample_records.values())
    sample_count = len(samples)
    names = ["chemical", "ntp", "nep", "none"]
    counts = [sum(x["best"] == name for x in samples) for name in names]
    fig, ax = plt.subplots(figsize=(8, 4.5)); ax.bar(names, counts, color=[PALETTE.get(n, "#777") for n in names])
    ax.set(title="Selected architecture under declared joint stress-test assumptions", ylabel=f"Samples out of {sample_count:,}")
    ax.text(0.01, -0.20, "These counts reflect assumed parameter distributions; they are not real-world probabilities.", transform=ax.transAxes, fontsize=9, color="#bbbbbb")
    ax.grid(axis="y", alpha=.18); fig.tight_layout(); fig.savefig(figures / "uncertainty_selection.svg"); fig.savefig(figures / "uncertainty_selection.png", dpi=180); plt.close(fig)


def make_trajectory_comparison(results: Path, figures: Path) -> None:
    """Contrast proxy status with actual propagated terminal constraints."""
    figures.mkdir(parents=True, exist_ok=True); _style()
    report = json.loads((results / "trajectory_comparison.json").read_text(encoding="utf-8"))
    t = report["trajectory"]
    # Gates live in the config and methodology; preserve explicit values here.
    values = [t["final_position_error_m"] / 5e8, t["final_velocity_error_m_s"] / 500]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), gridspec_kw={"width_ratios": [1, 1.7]})
    proxy_pass = int(report["screening_proxy"]["feasible"])
    trajectory_pass = int(t["success"])
    bars = axes[0].bar(["Screen proxy", "Trajectory gates"], [proxy_pass, trajectory_pass], color=["#d6a85d", "#65c7d0"])
    axes[0].set(title="Nominal NEP status", ylim=(0, 1.15), ylabel="Pass = 1")
    axes[0].bar_label(bars, labels=["pass" if proxy_pass else "fail", "pass" if trajectory_pass else "fail"])
    axes[0].grid(axis="y", alpha=.18)
    axes[1].scatter(["Position residual / gate", "Velocity residual / gate"], values, s=100, color="#65c7d0", zorder=3)
    axes[1].axhline(1, color="#d6a85d", linestyle="--", label="arrival gate")
    axes[1].set(title="Propagated terminal residuals", ylabel="Normalized residual (log scale)", yscale="log", ylim=(1e-6, 2))
    for i, value in enumerate(values): axes[1].annotate(f"{value:.2e}", (i, value), xytext=(0, 8), textcoords="offset points", ha="center")
    axes[1].grid(axis="y", alpha=.18); axes[1].legend(); fig.tight_layout()
    fig.savefig(figures / "trajectory_constraint_residuals.svg"); fig.savefig(figures / "trajectory_constraint_residuals.png", dpi=180); plt.close(fig)

    multistart_path = results / "trajectory_multistart.json"
    if multistart_path.exists():
        multi = json.loads(multistart_path.read_text(encoding="utf-8"))
        completed = [run for run in multi["runs"] if run.get("result") is not None]
        if completed:
            labels = [f"Start {run['start_index']}" for run in completed]
            propellant = [run["result"]["propellant_used_kg"] / 1000 for run in completed]
            converged = [bool(run["result"]["optimizer_converged"]) for run in completed]
            colors = ["#65c7d0" if value else "#d6a85d" for value in converged]
            fig, ax = plt.subplots(figsize=(8.5, 4.8))
            bars = ax.bar(labels, propellant, color=colors)
            ax.bar_label(bars, labels=[f"{value:.2f} t" for value in propellant], padding=3)
            subtitle = (f"{multi['terminal_gate_pass_count']}/{multi['completed_count']} pass gates; "
                        f"{multi['optimizer_converged_count']} optimizer-converged")
            ax.set(title=f"Initial-guess sensitivity — {subtitle}", ylabel="Propellant used [t]")
            ax.grid(axis="y", alpha=.18)
            fig.tight_layout()
            fig.savefig(figures / "trajectory_multistart_sensitivity.svg")
            fig.savefig(figures / "trajectory_multistart_sensitivity.png", dpi=180)
            plt.close(fig)
