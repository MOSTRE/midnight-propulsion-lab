import numpy as np
import pytest

from midnight_propulsion_lab.constants import SECONDS_PER_DAY
from midnight_propulsion_lab.trajectory import (
    TrajectoryBenchmark,
    default_control_guess,
    hohmann_arrival_state,
    hohmann_departure_state,
    propagate,
    propulsion_mass_state,
)
from midnight_propulsion_lab.mission import BASELINES, Scenario


def test_unpowered_hohmann_matches_analytical_two_body_endpoint():
    initial, transfer_time = hohmann_departure_state()
    benchmark = TrajectoryBenchmark(duration_days=transfer_time / SECONDS_PER_DAY)
    solution = propagate(benchmark, initial, 1_000, 500, 0, 0,
                         np.zeros(benchmark.segments), np.zeros(benchmark.segments))
    expected = hohmann_arrival_state()
    assert np.linalg.norm(solution.y[:2, -1] - expected[:2]) < 1.0
    assert np.linalg.norm(solution.y[2:4, -1] - expected[2:]) < 1e-5
    assert solution.y[4, -1] == 1_000


def test_nep_power_to_thrust_and_mass_flow_are_consistent():
    initial, dry, thrust, flow = propulsion_mass_state(Scenario(), BASELINES["nep"])
    assert initial > dry > 0
    assert thrust > 0
    assert np.isclose(flow, thrust / (BASELINES["nep"].isp_s * 9.80665))


def test_propellant_depletion_is_rejected():
    initial, dry, thrust, flow = propulsion_mass_state(Scenario(), BASELINES["nep"])
    benchmark = TrajectoryBenchmark()
    with pytest.raises(RuntimeError, match="propellant depletion"):
        propagate(benchmark, np.array([1.495978707e11, 0, 0, 29_784.7]), initial, dry, thrust, flow,
                  np.zeros(benchmark.segments), np.ones(benchmark.segments))


def test_propagation_includes_control_boundaries_once_and_time_is_monotonic():
    initial, transfer_time = hohmann_departure_state()
    benchmark = TrajectoryBenchmark(duration_days=transfer_time / SECONDS_PER_DAY)
    solution = propagate(benchmark, initial, 1_000, 500, 0, 0,
                         np.zeros(benchmark.segments), np.zeros(benchmark.segments))

    assert np.all(np.diff(solution.t) > 0)
    assert solution.y.shape == (5, solution.t.size)
    for boundary_index in range(1, benchmark.segments):
        boundary = boundary_index * benchmark.duration_s / benchmark.segments
        assert np.count_nonzero(np.isclose(solution.t, boundary, rtol=0, atol=1e-6)) == 1


def test_propagation_rejects_out_of_range_throttle():
    initial, _ = hohmann_departure_state()
    benchmark = TrajectoryBenchmark()
    throttles = np.zeros(benchmark.segments)
    throttles[2] = 1.01
    with pytest.raises(ValueError, match=r"throttles must be within \[0, 1\]"):
        propagate(benchmark, initial, 1_000, 500, 1.0, 0.0,
                  np.zeros(benchmark.segments), throttles)



def test_default_control_guess_has_valid_bounds_and_expected_shape():
    guess = default_control_guess(8)
    assert guess.shape == (16,)
    assert np.all(np.isfinite(guess))
    assert np.all(guess[:8] >= -np.pi) and np.all(guess[:8] <= np.pi)
    assert np.all(guess[8:] >= 0) and np.all(guess[8:] <= 1)
