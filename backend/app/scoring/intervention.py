"""
Shade intervention simulation.

Simulates the impact of adding a shade structure to a bus stop
using planning assumption scenarios (conservative, moderate, high).

These are NOT engineering guarantees.
"""

from __future__ import annotations

from app.config import settings, InterventionScenarioConfig


def get_scenario_config(scenario: str) -> InterventionScenarioConfig:
    """Get intervention scenario configuration by name."""
    configs = {
        "conservative": settings.intervention.conservative,
        "moderate": settings.intervention.moderate,
        "high": settings.intervention.high,
    }
    if scenario not in configs:
        raise ValueError(f"Unknown scenario: {scenario}. Use: {list(configs.keys())}")
    return configs[scenario]


def simulate_shade_intervention(
    baseline_dangerous_minutes: float,
    baseline_cumulative_exceedance: float,
    baseline_heat_score: float,
    baseline_priority_score: float,
    baseline_rank: int,
    all_baseline_priority_scores: list[float],
    scenario: str = "moderate",
    weights: dict[str, float] | None = None,
    shade_score: float = 50.0,
    vulnerability_score: float = 50.0,
    transit_score: float = 50.0,
) -> dict:
    """
    Simulate the impact of a shade structure on a single bus stop.

    The simulation reduces exposure metrics by the scenario's effectiveness
    and coverage factors, then recalculates the heat score and priority.

    Args:
        baseline_dangerous_minutes: Current dangerous minutes.
        baseline_cumulative_exceedance: Current cumulative exceedance.
        baseline_heat_score: Current heat component score (0–100).
        baseline_priority_score: Current final priority score.
        baseline_rank: Current rank.
        all_baseline_priority_scores: All stops' priority scores for re-ranking.
        scenario: 'conservative', 'moderate', or 'high'.
        weights: Priority weight overrides.
        shade_score, vulnerability_score, transit_score: Other components.

    Returns:
        Dict with baseline, projected, and delta metrics.
    """
    config = get_scenario_config(scenario)

    reduction_factor = config.effectiveness_factor * config.coverage_factor

    # Calculate avoided exposure
    avoided_minutes = baseline_dangerous_minutes * reduction_factor
    avoided_exceedance = baseline_cumulative_exceedance * reduction_factor

    projected_minutes = baseline_dangerous_minutes - avoided_minutes
    projected_exceedance = baseline_cumulative_exceedance - avoided_exceedance

    # Reduce heat score proportionally
    projected_heat_score = max(0.0, baseline_heat_score * (1 - reduction_factor))

    # Recalculate priority with reduced heat score
    w = weights or {
        "heat": settings.scoring_weights.heat,
        "shade": settings.scoring_weights.shade,
        "vulnerability": settings.scoring_weights.vulnerability,
        "transit": settings.scoring_weights.transit,
    }

    # After shade intervention, the shade score also improves
    projected_shade_score = max(0.0, shade_score * 0.5)  # 50% improvement

    projected_priority = (
        w["heat"] * projected_heat_score
        + w["shade"] * projected_shade_score
        + w["vulnerability"] * vulnerability_score
        + w["transit"] * transit_score
    )
    projected_priority = round(projected_priority, 2)

    # Estimate new rank
    projected_rank = 1
    for other_score in all_baseline_priority_scores:
        if other_score > projected_priority:
            projected_rank += 1

    rank_change = baseline_rank - projected_rank  # Positive = improved

    percentage_reduction = (
        (avoided_minutes / baseline_dangerous_minutes * 100)
        if baseline_dangerous_minutes > 0
        else 0.0
    )

    return {
        # Baseline
        "baseline_dangerous_minutes": round(baseline_dangerous_minutes, 1),
        "baseline_cumulative_exceedance": round(baseline_cumulative_exceedance, 2),
        "baseline_heat_score": round(baseline_heat_score, 2),
        "baseline_priority_score": round(baseline_priority_score, 2),
        "baseline_rank": baseline_rank,
        # Projected
        "projected_dangerous_minutes": round(projected_minutes, 1),
        "projected_cumulative_exceedance": round(projected_exceedance, 2),
        "projected_heat_score": round(projected_heat_score, 2),
        "projected_priority_score": projected_priority,
        "projected_rank": projected_rank,
        # Deltas
        "avoided_dangerous_minutes": round(avoided_minutes, 1),
        "avoided_cumulative_exceedance": round(avoided_exceedance, 2),
        "percentage_reduction": round(percentage_reduction, 1),
        "rank_change": rank_change,
        # Metadata
        "scenario": scenario,
        "effectiveness_factor": config.effectiveness_factor,
        "coverage_factor": config.coverage_factor,
        "confidence": 0.7,
        "disclaimer": (
            "These are planning assumptions for comparison purposes. "
            "They are not engineering guarantees of temperature reduction."
        ),
    }
