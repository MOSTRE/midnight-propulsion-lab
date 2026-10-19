from midnight_propulsion_lab.mission import BASELINES, Scenario, evaluate


def test_results_keep_mass_nonnegative():
    for architecture in BASELINES.values():
        result = evaluate(Scenario(), architecture)
        assert result.propellant_kg >= 0
        assert result.dry_mass_kg > 0


def test_nep_reports_time_proxy():
    result = evaluate(Scenario(), BASELINES["nep"])
    assert result.required_acceleration_m_s2 > 0
    assert result.thrust_n > 0
