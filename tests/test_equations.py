from math import isclose

from midnight_propulsion_lab.constants import G0_M_S2
from midnight_propulsion_lab.mission import exhaust_velocity, nep_radiator, propellant_for_delta_v


def test_exhaust_velocity_definition():
    assert isclose(exhaust_velocity(1), G0_M_S2)


def test_zero_delta_v_needs_no_propellant():
    assert propellant_for_delta_v(0, 450, 1000, 0.05) == 0


def test_radiator_scales_with_waste_heat():
    area, mass = nep_radiator(100, 0.25, 800, .85, 6)
    assert area > 0 and mass == area * 6
