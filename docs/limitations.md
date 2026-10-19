# Limitations

- Equivalent delta-v does not make chemical, NTP, and low-thrust NEP trajectories equivalent.
- No gravity losses, launch injection, duty cycle, degradation, reliability, shielding geometry, cryogenic boil-off, or detailed thermal loop is modeled.
- The NEP uncertainty distributions are stress-test assumptions, not fitted data.
- Specific mass and radiator mass may overlap in real studies; this model separates them only by user-declared bookkeeping. The baseline deliberately treats power-specific mass as reactor/conversion/PMAD and adds a radiator estimate; users must avoid double counting when replacing values.
- The result cannot establish novelty, engineering readiness, safety, cost, or patentability.
