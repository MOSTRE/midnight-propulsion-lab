from __future__ import annotations

import argparse
from pathlib import Path

from .experiments import run_all
from .experiments import run_trajectory, run_trajectory_multistart
from .plotting import make_figures, make_trajectory_comparison

def main() -> None:
    parser = argparse.ArgumentParser(description="Midnight Propulsion Lab screening experiments")
    parser.add_argument("command", choices=["run", "figures", "trajectory", "trajectory-figures", "trajectory-multistart"])
    parser.add_argument("--samples", type=int, default=2000)
    parser.add_argument("--starts", type=int, default=3, help="initial guesses for trajectory-multistart")
    parser.add_argument("--max-nfev", type=int, default=40, help="function-evaluation budget per trajectory start")
    parser.add_argument("--seed", type=int, default=20261019)
    parser.add_argument("--results", type=Path, default=Path("results"))
    parser.add_argument("--figures", type=Path, default=Path("figures"))
    args = parser.parse_args()
    if args.command == "run": print(run_all(args.results, args.samples, args.seed))
    elif args.command == "figures": make_figures(args.results, args.figures)
    elif args.command == "trajectory": print(run_trajectory(args.results))
    elif args.command == "trajectory-figures": make_trajectory_comparison(args.results, args.figures)
    else: print(run_trajectory_multistart(args.results, starts=args.starts, seed=args.seed, max_nfev=args.max_nfev))

if __name__ == "__main__": main()
