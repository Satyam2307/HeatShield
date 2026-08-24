"""Tests for intervention simulation."""

from app.scoring.intervention import simulate_shade_intervention, get_scenario_config
import pytest


def test_scenario_configs():
    c = get_scenario_config("conservative")
    assert c.effectiveness_factor == 0.20
    assert c.coverage_factor == 0.70

    m = get_scenario_config("moderate")
    assert m.effectiveness_factor == 0.35
    assert m.coverage_factor == 0.80

    h = get_scenario_config("high")
    assert h.effectiveness_factor == 0.50
    assert h.coverage_factor == 0.90


def test_invalid_scenario():
    with pytest.raises(ValueError):
        get_scenario_config("extreme")


def test_moderate_simulation():
    result = simulate_shade_intervention(
        baseline_dangerous_minutes=300.0,
        baseline_cumulative_exceedance=25.0,
        baseline_heat_score=85.0,
        baseline_priority_score=80.0,
        baseline_rank=3,
        all_baseline_priority_scores=[90.0, 85.0, 70.0, 60.0],
        scenario="moderate",
        shade_score=75.0,
        vulnerability_score=60.0,
        transit_score=50.0,
    )

    # Moderate: effectiveness=0.35, coverage=0.80 → reduction=28%
    assert result["percentage_reduction"] == 28.0
    assert result["projected_dangerous_minutes"] < 300.0
    assert result["projected_priority_score"] < 80.0
    assert result["avoided_dangerous_minutes"] > 0
    assert result["disclaimer"]  # Must include disclaimer


def test_conservative_reduces_less():
    conservative = simulate_shade_intervention(
        baseline_dangerous_minutes=300.0,
        baseline_cumulative_exceedance=25.0,
        baseline_heat_score=85.0,
        baseline_priority_score=80.0,
        baseline_rank=3,
        all_baseline_priority_scores=[90.0, 85.0],
        scenario="conservative",
    )
    moderate = simulate_shade_intervention(
        baseline_dangerous_minutes=300.0,
        baseline_cumulative_exceedance=25.0,
        baseline_heat_score=85.0,
        baseline_priority_score=80.0,
        baseline_rank=3,
        all_baseline_priority_scores=[90.0, 85.0],
        scenario="moderate",
    )
    assert conservative["avoided_dangerous_minutes"] < moderate["avoided_dangerous_minutes"]


def test_zero_baseline():
    result = simulate_shade_intervention(
        baseline_dangerous_minutes=0.0,
        baseline_cumulative_exceedance=0.0,
        baseline_heat_score=0.0,
        baseline_priority_score=10.0,
        baseline_rank=100,
        all_baseline_priority_scores=[20.0, 15.0],
        scenario="moderate",
    )
    assert result["percentage_reduction"] == 0.0
    assert result["projected_dangerous_minutes"] == 0.0
