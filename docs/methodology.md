# Methodology

The study uses a deliberately low-fidelity common scenario: fixed initial mass,
payload, equivalent delta-v, duration, reserve fraction, and bus mass. Chemical
and NTP use an impulsive-equivalent mass screen. NEP also includes a power-system
term, an ideal radiator estimate, electric-thruster mass, ideal electric thrust,
and a necessary average-acceleration check. The parameter sweep is deterministic.

The Monte Carlo experiment samples mission mass, equivalent delta-v, duration,
NEP power-system specific mass, radiator areal density, and thruster efficiency.
The fixed seed is 20261019. A sample selects the feasible architecture with the
largest mass margin; ties are not treated as a special result. These distributions
are deliberately broad stress-test assumptions, not calibrated probability models.

This setup asks whether a nominal decision is robust enough to justify a more
expensive trajectory study. It cannot compare mission completion probability.
