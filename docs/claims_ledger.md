# Claims ledger

| Claim | Classification | Evidence | Limitation |
| --- | --- | --- | --- |
| \(\Delta v=v_e\ln(m_0/m_f)\) is used under ideal-rocket assumptions | Established background physics | `mission.py`, NASA rocket-equation source in bibliography | Not a low-thrust trajectory model |
| Radiator assumptions materially affect NEP mass | Established background | Machemer et al.; Kokan et al. | No detailed thermal-loop model here |
| Baseline NEP screen is feasible while baseline chemical/NTP are mass-infeasible | Model-derived result | `results/baseline.csv` | Depends entirely on declared generic inputs |
| Joint screen selects NEP 1,288/2,000 times, NTP 321/2,000, none 391/2,000 | Model-derived result | `results/summary.json`, seed 20261019 | Sample distributions are not empirical |
| A bounded-control NEP trajectory meets the circular-Mars surrogate arrival gates | Model-derived result | `results/trajectory_comparison.json`, `trajectory.py` | Local shooting solution; not a real ephemeris/capture trajectory |
| The generic screen's nominal NEP conclusion changes under this benchmark | Unsupported claim—removed | `docs/trajectory_comparison.md` | No matched high-fidelity architecture comparison or Monte Carlo rerun |
| The software identifies a new architecture method | Unsupported claim—removed | First-pass prior-art screen | Existing integrated and robust methods exist |
| The approach is patentable or novel | Unverified hypothesis | `research/prior_art_matrix.csv` | No exhaustive prior-art search |
