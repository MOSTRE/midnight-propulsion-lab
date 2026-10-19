"""Transparent algebraic mass and thrust screen.

The model applies the ideal rocket equation to a specified equivalent mission
delta-v.  NEP time feasibility is only a constant-thrust acceleration proxy:
it is not a low-thrust trajectory optimization and must not be read as one.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import exp
from typing import Literal

from .constants import G0_M_S2, SECONDS_PER_DAY, SIGMA_W_M2_K4


@dataclass(frozen=True)
class Scenario:
    initial_mass_kg: float = 20_000.0
    payload_kg: float = 2_000.0
    delta_v_m_s: float = 9_000.0
    duration_days: float = 365.0
    reserve_fraction: float = 0.05
    bus_structure_kg: float = 1_200.0


@dataclass(frozen=True)
class Architecture:
    name: Literal["chemical", "ntp", "nep"]
    isp_s: float
    fixed_dry_mass_kg: float
    tank_fraction_of_propellant: float
    # NEP-only inputs. They remain zero for impulsive systems.
    electric_power_kw: float = 0.0
    efficiency: float = 0.0
    power_specific_mass_kg_kw: float = 0.0
    conversion_efficiency: float = 0.0
    radiator_temperature_k: float = 0.0
    radiator_areal_density_kg_m2: float = 0.0
    radiator_effectiveness: float = 0.85
    thruster_specific_mass_kg_kw: float = 0.0


@dataclass(frozen=True)
class Result:
    architecture: str
    feasible: bool
    reason: str
    payload_margin_kg: float
    propellant_kg: float
    dry_mass_kg: float
    thrust_n: float
    acceleration_m_s2: float
    required_acceleration_m_s2: float
    radiator_area_m2: float
    radiator_mass_kg: float
    power_system_mass_kg: float
    mass_ratio: float

    def record(self) -> dict[str, float | bool | str]:
        return asdict(self)


def exhaust_velocity(isp_s: float) -> float:
    if isp_s <= 0:
        raise ValueError("specific impulse must be positive")
    return isp_s * G0_M_S2


def propellant_for_delta_v(dv_m_s: float, isp_s: float, final_mass_kg: float, reserve: float) -> float:
    """Ideal impulsive-equivalent propellant including a multiplicative reserve."""
    if min(dv_m_s, final_mass_kg) < 0 or not 0 <= reserve < 1:
        raise ValueError("invalid mass, delta-v, or reserve")
    ideal = final_mass_kg * (exp(dv_m_s / exhaust_velocity(isp_s)) - 1.0)
    return ideal / (1.0 - reserve)


def nep_radiator(power_kw: float, conversion_efficiency: float, temperature_k: float,
                 effectiveness: float, areal_density: float) -> tuple[float, float]:
    """Blackbody radiator lower-order estimate; returns (area, mass).

    Waste heat is P_e(1/eta_c - 1); two-sided, geometry, plumbing and view
    effects are intentionally absorbed in effectiveness and areal density.
    """
    if not (power_kw > 0 and 0 < conversion_efficiency <= 1 and temperature_k > 0
            and 0 < effectiveness <= 1 and areal_density >= 0):
        raise ValueError("invalid NEP thermal parameters")
    waste_w = power_kw * 1_000.0 * (1.0 / conversion_efficiency - 1.0)
    area = waste_w / (effectiveness * SIGMA_W_M2_K4 * temperature_k**4)
    return area, area * areal_density


def _nep_dry(arch: Architecture) -> tuple[float, float, float]:
    area, radiator_mass = nep_radiator(arch.electric_power_kw, arch.conversion_efficiency,
                                       arch.radiator_temperature_k, arch.radiator_effectiveness,
                                       arch.radiator_areal_density_kg_m2)
    power_mass = arch.electric_power_kw * arch.power_specific_mass_kg_kw
    thruster_mass = arch.electric_power_kw * arch.thruster_specific_mass_kg_kw
    return power_mass + thruster_mass + radiator_mass, area, radiator_mass


def evaluate(scenario: Scenario, architecture: Architecture) -> Result:
    """Close a self-consistent tank/propellant mass loop by fixed-point iteration."""
    if scenario.initial_mass_kg <= 0 or scenario.duration_days <= 0 or scenario.payload_kg < 0:
        raise ValueError("invalid scenario")
    ve = exhaust_velocity(architecture.isp_s)
    if architecture.name == "nep":
        subsystem, radiator_area, radiator_mass = _nep_dry(architecture)
        power_system_mass = architecture.electric_power_kw * architecture.power_specific_mass_kg_kw
        thrust = 2 * architecture.efficiency * architecture.electric_power_kw * 1_000.0 / ve
    else:
        subsystem = radiator_area = radiator_mass = power_system_mass = thrust = 0.0
    fixed = scenario.payload_kg + scenario.bus_structure_kg + architecture.fixed_dry_mass_kg + subsystem
    # With tank mass = k*m_p, the mass closure is m_p = r(fixed + k*m_p),
    # so m_p = r*fixed/(1-r*k).  A non-positive denominator is physically
    # impossible for this declared tank fraction, not a numerical failure.
    r = (exp(scenario.delta_v_m_s / ve) - 1.0) / (1.0 - scenario.reserve_fraction)
    denominator = 1.0 - r * architecture.tank_fraction_of_propellant
    if denominator <= 0:
        return Result(architecture.name, False, "tank/propellant mass loop has no finite solution",
                      float("nan"), float("nan"), float("nan"), thrust, 0.0,
                      scenario.delta_v_m_s / (scenario.duration_days * SECONDS_PER_DAY), radiator_area,
                      radiator_mass, power_system_mass, float("nan"))
    propellant = r * fixed / denominator
    tank_mass = architecture.tank_fraction_of_propellant * propellant
    dry = fixed + tank_mass
    wet = dry + propellant
    required_acceleration = scenario.delta_v_m_s / (scenario.duration_days * SECONDS_PER_DAY)
    acceleration = thrust / wet if wet > 0 else 0.0
    mass_ok = wet <= scenario.initial_mass_kg
    time_ok = architecture.name != "nep" or acceleration >= required_acceleration
    reason = "feasible" if mass_ok and time_ok else ("exceeds initial mass" if not mass_ok else "fails constant-thrust acceleration proxy")
    return Result(architecture.name, mass_ok and time_ok, reason, scenario.initial_mass_kg - wet,
                  propellant, dry, thrust, acceleration, required_acceleration, radiator_area,
                  radiator_mass, power_system_mass, wet / dry)


BASELINES = {
    "chemical": Architecture("chemical", 450, 900, 0.08),
    "ntp": Architecture("ntp", 900, 2_400, 0.14),
    "nep": Architecture("nep", 4_000, 500, 0.08, electric_power_kw=1_000, efficiency=0.60,
                        power_specific_mass_kg_kw=8.0, conversion_efficiency=0.25,
                        radiator_temperature_k=800, radiator_areal_density_kg_m2=6.0,
                        thruster_specific_mass_kg_kw=0.25),
}
