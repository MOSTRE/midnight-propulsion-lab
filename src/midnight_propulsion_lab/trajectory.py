"""Planar, Sun-centered, bounded-thrust trajectory validation experiment.

This is deliberately a circular-coplanar benchmark, not an operational Earth-Mars
mission analysis. Earth and Mars are prescribed circular markers; their gravity,
planetary escape/capture, ephemerides, and launch/insertion systems are omitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import atan2, cos, pi, sin, sqrt

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import least_squares

from .constants import EARTH_ORBIT_RADIUS_M, MARS_ORBIT_RADIUS_M, MU_SUN_M3_S2, SECONDS_PER_DAY
from .mission import Architecture, Scenario, _nep_dry, exhaust_velocity


@dataclass(frozen=True)
class TrajectoryBenchmark:
    """Circular-coplanar Earth-to-Mars rendezvous surrogate in an inertial frame."""
    duration_days: float = 365.0
    segments: int = 8
    position_tolerance_m: float = 5e8  # 500,000 km: screening-grade arrival gate
    velocity_tolerance_m_s: float = 500.0
    rtol: float = 1e-10
    atol: float = 1e-3

    def __post_init__(self) -> None:
        if self.duration_days <= 0:
            raise ValueError("duration_days must be positive")
        if self.segments < 1:
            raise ValueError("segments must be at least 1")
        if self.position_tolerance_m <= 0 or self.velocity_tolerance_m_s <= 0:
            raise ValueError("terminal tolerances must be positive")
        if self.rtol <= 0 or self.atol <= 0:
            raise ValueError("integration tolerances must be positive")

    @property
    def duration_s(self) -> float:
        return self.duration_days * SECONDS_PER_DAY

    @property
    def earth_mean_motion(self) -> float:
        return sqrt(MU_SUN_M3_S2 / EARTH_ORBIT_RADIUS_M**3)

    @property
    def mars_mean_motion(self) -> float:
        return sqrt(MU_SUN_M3_S2 / MARS_ORBIT_RADIUS_M**3)

    @property
    def mars_initial_phase_rad(self) -> float:
        # The classical Hohmann phase angle is an independently checkable
        # reference phase, retained while the powered case has a 365-day TOF.
        a = (EARTH_ORBIT_RADIUS_M + MARS_ORBIT_RADIUS_M) / 2
        h_time = pi * sqrt(a**3 / MU_SUN_M3_S2)
        return pi - self.mars_mean_motion * h_time


@dataclass(frozen=True)
class TrajectoryResult:
    # `success` means the configured terminal gates passed; optimizer convergence
    # is reported independently and must not be inferred from this flag.
    success: bool
    optimizer_converged: bool
    optimizer_status: int
    optimizer_cost: float
    optimizer_optimality: float
    message: str
    final_position_error_m: float
    final_velocity_error_m_s: float
    final_mass_kg: float
    propellant_used_kg: float
    max_thrust_n: float
    dry_mass_kg: float
    duration_days: float
    nfev: int
    controls: tuple[float, ...]

    def record(self) -> dict:
        return self.__dict__ | {"controls": list(self.controls)}


def circular_state(radius_m: float, angle_rad: float) -> np.ndarray:
    speed = sqrt(MU_SUN_M3_S2 / radius_m)
    return np.array([radius_m * cos(angle_rad), radius_m * sin(angle_rad),
                     -speed * sin(angle_rad), speed * cos(angle_rad)])


def target_mars_state(benchmark: TrajectoryBenchmark) -> np.ndarray:
    return circular_state(MARS_ORBIT_RADIUS_M,
                          benchmark.mars_initial_phase_rad + benchmark.mars_mean_motion * benchmark.duration_s)


def hohmann_departure_state() -> tuple[np.ndarray, float]:
    """Analytical unpowered reference state and half-ellipse transfer time."""
    a = (EARTH_ORBIT_RADIUS_M + MARS_ORBIT_RADIUS_M) / 2
    v_depart = sqrt(MU_SUN_M3_S2 * (2 / EARTH_ORBIT_RADIUS_M - 1 / a))
    transfer_time = pi * sqrt(a**3 / MU_SUN_M3_S2)
    return np.array([EARTH_ORBIT_RADIUS_M, 0.0, 0.0, v_depart]), transfer_time


def hohmann_arrival_state() -> np.ndarray:
    """Analytical state at the aphelion of the Earth-to-Mars Hohmann ellipse."""
    a = (EARTH_ORBIT_RADIUS_M + MARS_ORBIT_RADIUS_M) / 2
    v_arrive = sqrt(MU_SUN_M3_S2 * (2 / MARS_ORBIT_RADIUS_M - 1 / a))
    return np.array([-MARS_ORBIT_RADIUS_M, 0.0, 0.0, -v_arrive])


def propulsion_mass_state(scenario: Scenario, architecture: Architecture) -> tuple[float, float, float, float]:
    """Return (initial mass, dry cutoff, thrust, mass flow) for the new experiment.

    The screening model's component bookkeeping is preserved. Unlike the screen,
    all unused launch margin is modeled as usable propellant capacity; the result
    is therefore a *separate* benchmark and is never substituted into its table.
    """
    if architecture.name != "nep":
        raise ValueError("trajectory experiment currently implements NEP only")
    subsystem, _, _ = _nep_dry(architecture)
    dry = scenario.payload_kg + scenario.bus_structure_kg + architecture.fixed_dry_mass_kg + subsystem
    initial = scenario.initial_mass_kg
    if initial <= dry:
        raise ValueError("initial mass must exceed fixed trajectory dry mass")
    ve = exhaust_velocity(architecture.isp_s)
    thrust = 2 * architecture.efficiency * architecture.electric_power_kw * 1_000.0 / ve
    return initial, dry, thrust, thrust / ve


@dataclass(frozen=True)
class PropagationResult:
    """Combined state history from segment-by-segment integration."""
    t: np.ndarray
    y: np.ndarray
    success: bool
    message: str


def _rhs(_t: float, state: np.ndarray, angle: float, throttle: float,
         thrust_n: float, mdot_kg_s: float) -> np.ndarray:
    """State derivative for one fixed-control segment.

    Each control segment is integrated separately so an adaptive solver never
    evaluates a Runge-Kutta step across an abrupt control discontinuity.
    """
    x, y_pos, vx, vy, mass = state
    radius_cubed = (x * x + y_pos * y_pos) ** 1.5
    direction = atan2(vy, vx) + angle
    tx = throttle * thrust_n * cos(direction)
    ty = throttle * thrust_n * sin(direction)
    return np.array([
        vx,
        vy,
        -MU_SUN_M3_S2 * x / radius_cubed + tx / mass,
        -MU_SUN_M3_S2 * y_pos / radius_cubed + ty / mass,
        -throttle * mdot_kg_s,
    ])


def propagate(benchmark: TrajectoryBenchmark, initial_state: np.ndarray, initial_mass_kg: float,
              dry_mass_kg: float, thrust_n: float, mdot_kg_s: float,
              angles: np.ndarray, throttles: np.ndarray) -> PropagationResult:
    """Integrate r, v, m with DOP853, stopping exactly at control boundaries.

    A separate integration is performed on every piecewise-constant control
    arc. This is important: integrating over a discontinuous right-hand side
    can make adaptive error estimates misleading, especially in long arcs.
    Propellant depletion is handled as a terminal event rather than allowing a
    solver step to cross the dry-mass boundary.
    """
    if len(angles) != benchmark.segments or len(throttles) != benchmark.segments:
        raise ValueError("one angle and throttle required per segment")
    if not np.all(np.isfinite(angles)) or not np.all(np.isfinite(throttles)):
        raise ValueError("controls must be finite")
    if np.any(throttles < 0.0) or np.any(throttles > 1.0):
        raise ValueError("throttles must be within [0, 1]")
    if initial_mass_kg <= dry_mass_kg:
        raise ValueError("initial mass must exceed dry mass")
    if dry_mass_kg <= 0.0 or thrust_n < 0.0 or mdot_kg_s < 0.0:
        raise ValueError("dry mass must be positive and thrust/flow nonnegative")

    segment_duration = benchmark.duration_s / benchmark.segments
    state = np.asarray(np.r_[initial_state, initial_mass_kg], dtype=float)
    time_parts: list[np.ndarray] = []
    state_parts: list[np.ndarray] = []

    def dry_mass_event(_t: float, y: np.ndarray) -> float:
        return float(y[4] - dry_mass_kg)

    dry_mass_event.terminal = True
    dry_mass_event.direction = -1

    for index, (angle, throttle) in enumerate(zip(angles, throttles, strict=True)):
        t_start = index * segment_duration
        t_end = (index + 1) * segment_duration

        def segment_rhs(t: float, y: np.ndarray) -> np.ndarray:
            return _rhs(t, y, float(angle), float(throttle), thrust_n, mdot_kg_s)

        solution = solve_ivp(
            segment_rhs,
            (t_start, t_end),
            state,
            method="DOP853",
            events=dry_mass_event,
            rtol=benchmark.rtol,
            atol=benchmark.atol,
            max_step=segment_duration / 8,
        )
        if not solution.success:
            raise RuntimeError(solution.message)
        if solution.t_events[0].size:
            raise RuntimeError("propellant depletion constraint violated")
        if index:
            # The first state of each segment duplicates the preceding segment's
            # endpoint; drop it so the returned history has strictly increasing t.
            time_parts.append(solution.t[1:])
            state_parts.append(solution.y[:, 1:])
        else:
            time_parts.append(solution.t)
            state_parts.append(solution.y)
        state = solution.y[:, -1]

    return PropagationResult(
        t=np.concatenate(time_parts),
        y=np.concatenate(state_parts, axis=1),
        success=True,
        message="All control segments integrated successfully.",
    )


def default_control_guess(segments: int) -> np.ndarray:
    """Return the documented baseline shooting guess: early thrust then coast/brake."""
    if segments < 1:
        raise ValueError("segments must be at least 1")
    throttle = np.full(segments, 0.01, dtype=float)
    throttle[: min(2, segments)] = 0.40
    return np.r_[np.zeros(segments, dtype=float), throttle]


def solve_nep_benchmark(scenario: Scenario, architecture: Architecture, benchmark: TrajectoryBenchmark = TrajectoryBenchmark(),
                        max_nfev: int = 100, initial_controls: np.ndarray | None = None) -> TrajectoryResult:
    """Bounded least-squares shooting for terminal r/v, with throttle-use regularization.

    This is an experimental feasibility search, not proof of a globally optimal
    control solution. The steering offset is constant relative to instantaneous
    velocity within each arc; the actual thrust direction therefore rotates with
    the velocity vector.
    """
    initial_mass, dry_mass, thrust, mdot = propulsion_mass_state(scenario, architecture)
    initial_state = circular_state(EARTH_ORBIT_RADIUS_M, 0.0)
    target = target_mars_state(benchmark)
    n = benchmark.segments

    def residual(z: np.ndarray) -> np.ndarray:
        angles, throttles = z[:n], z[n:]
        try:
            sol = propagate(benchmark, initial_state, initial_mass, dry_mass, thrust, mdot, angles, throttles)
            final = sol.y[:4, -1]
            terminal = np.r_[(final[:2] - target[:2]) / benchmark.position_tolerance_m,
                             (final[2:] - target[2:]) / benchmark.velocity_tolerance_m_s]
            # A small regularizer chooses a lower-duty solution among terminal fits.
            return np.r_[terminal, 0.01 * throttles]
        except RuntimeError:
            return np.full(4 + n, 1e6)

    # Controls are offsets from the instantaneous velocity direction. Alternative
    # initial guesses are accepted so local-initialization sensitivity can be tested.
    if initial_controls is None:
        z0 = default_control_guess(n)
    else:
        z0 = np.asarray(initial_controls, dtype=float).copy()
        if z0.shape != (2 * n,) or not np.all(np.isfinite(z0)):
            raise ValueError("initial_controls must contain 2 * segments finite values")
        if np.any(z0[:n] < -pi) or np.any(z0[:n] > pi):
            raise ValueError("initial steering offsets must lie within [-pi, pi]")
        if np.any(z0[n:] < 0.0) or np.any(z0[n:] > 1.0):
            raise ValueError("initial throttles must lie within [0, 1]")
    fit = least_squares(residual, z0, bounds=(np.r_[np.full(n, -pi), np.zeros(n)],
                                               np.r_[np.full(n, pi), np.ones(n)]),
                        max_nfev=max_nfev, xtol=1e-8, ftol=1e-8, gtol=1e-8,
                        x_scale="jac", diff_step=1e-3, verbose=0)
    angles, throttles = fit.x[:n], fit.x[n:]
    sol = propagate(benchmark, initial_state, initial_mass, dry_mass, thrust, mdot, angles, throttles)
    final = sol.y[:4, -1]
    position_error = float(np.linalg.norm(final[:2] - target[:2]))
    velocity_error = float(np.linalg.norm(final[2:] - target[2:]))
    success = position_error <= benchmark.position_tolerance_m and velocity_error <= benchmark.velocity_tolerance_m_s
    return TrajectoryResult(
        success=success,
        optimizer_converged=bool(fit.success),
        optimizer_status=int(fit.status),
        optimizer_cost=float(fit.cost),
        optimizer_optimality=float(fit.optimality),
        message=str(fit.message),
        final_position_error_m=position_error,
        final_velocity_error_m_s=velocity_error,
        final_mass_kg=float(sol.y[4, -1]),
        propellant_used_kg=float(initial_mass - sol.y[4, -1]),
        max_thrust_n=thrust,
        dry_mass_kg=dry_mass,
        duration_days=benchmark.duration_days,
        nfev=int(fit.nfev),
        controls=tuple(float(x) for x in fit.x),
    )
