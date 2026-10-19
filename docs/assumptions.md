# Assumptions register

The baseline uses 20,000 kg initial mass, 2,000 kg payload, 9 km/s equivalent
delta-v, 365 days, and 5% propellant reserve. Isp values are 450 s chemical,
900 s NTP, and 4,000 s NEP. These are scenario assumptions—not claimed vehicle
specifications. The NEP case assumes 1 MWe electric input, 60% thruster
efficiency, 25% conversion efficiency, 8 kg/kWe non-radiator power-system mass,
800 K radiator, 6 kg/m² radiator density, and 0.25 kg/kWe thruster mass.

The power-specific-mass field explicitly excludes the modeled radiator. This
bookkeeping rule is necessary to avoid double counting but must be checked anew
when substituting literature values.

## Trajectory benchmark additions

The trajectory experiment preserves the NEP subsystem calculation but uses the
declared 20,000 kg as its initial propagated mass and a fixed dry cutoff of
12,861.8 kg. The remaining mass is usable propellant capacity. This differs from
the screening model's tank/propellant closed-form allocation and is recorded as a
separate benchmark, not a replacement. The solar-system model is circular and
coplanar with solar gravity only; all operational planetary effects are omitted.
