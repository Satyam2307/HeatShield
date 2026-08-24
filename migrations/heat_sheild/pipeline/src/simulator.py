"""
Shade Intervention Simulator for Hartford Bus Stops.
Calculates exposure reduction, avoided dangerous minutes, projected scores, and rank changes.
"""

from typing import Dict, Any, List

SCENARIO_CONFIGS = {
    "conservative": {"effectiveness_factor": 0.20, "coverage_factor": 1.0, "description": "Basic single-bench canopy structure (20% heat exposure reduction)"},
    "moderate": {"effectiveness_factor": 0.35, "coverage_factor": 1.0, "description": "Standard high-durability transit shelter (35% heat exposure reduction)"},
    "high": {"effectiveness_factor": 0.50, "coverage_factor": 1.0, "description": "Full green-roof solar shade structure + misting option (50% heat exposure reduction)"}
}

def simulate_stop_intervention(
    stop_data: Dict[str, Any],
    all_stops: List[Dict[str, Any]],
    scenario: str = "moderate",
    weights: Dict[str, float] = None
) -> Dict[str, Any]:
    """
    Simulate shade intervention on a single bus stop and re-calculate rank among all stops.
    """
    cfg = SCENARIO_CONFIGS.get(scenario.lower(), SCENARIO_CONFIGS["moderate"])
    eff = cfg["effectiveness_factor"]
    
    # Safely extract metrics whether flat or nested under 'metrics'
    metrics = stop_data.get("metrics", {})
    baseline_dangerous_mins = float(metrics.get("dangerous_minutes", stop_data.get("dangerous_minutes", 0)))
    baseline_exceedance = float(metrics.get("cumulative_exceedance", stop_data.get("cumulative_exceedance", 0)))
    baseline_persistence = float(metrics.get("persistence_minutes", stop_data.get("persistence_minutes", 0)))
    
    components = stop_data.get("components", {})
    baseline_heat_score = float(components.get("heat", stop_data.get("heat_score", 0)))
    baseline_shade_score = float(components.get("shade", stop_data.get("shade_score", 0)))
    baseline_vulnerability_score = float(components.get("vulnerability", stop_data.get("vulnerability_score", 0)))
    baseline_transit_score = float(components.get("transit", stop_data.get("transit_score", 0)))
    
    baseline_priority_score = float(stop_data.get("priority_score", 0))
    baseline_rank = int(stop_data.get("rank", 1))
    
    # Avoided & projected metrics
    avoided_dangerous_mins = round(baseline_dangerous_mins * eff, 1)
    projected_dangerous_mins = round(max(0.0, baseline_dangerous_mins - avoided_dangerous_mins), 1)
    
    projected_exceedance = round(max(0.0, baseline_exceedance * (1.0 - eff)), 2)
    projected_persistence = round(max(0.0, baseline_persistence * (1.0 - eff)), 1)
    
    # Projected heat score reduction
    projected_heat_score = round(max(10.0, baseline_heat_score * (1.0 - eff * 0.7)), 1)
    projected_shade_score = round(max(10.0, baseline_shade_score * (1.0 - eff * 0.8)), 1)
    
    w = weights or {"heat": 0.40, "shade": 0.25, "vulnerability": 0.20, "transit": 0.15}
    
    projected_priority_score = round(
        w["heat"] * projected_heat_score
        + w["shade"] * projected_shade_score
        + w["vulnerability"] * baseline_vulnerability_score
        + w["transit"] * baseline_transit_score, 1
    )
    
    # Estimate projected rank after score drop
    other_scores = [s.get("priority_score", 0) for s in all_stops if s.get("asset_id") != stop_data.get("asset_id")]
    higher_count = sum(1 for s in other_scores if s > projected_priority_score)
    projected_rank = higher_count + 1
    rank_change = projected_rank - baseline_rank  # positive number means drop in priority rank (e.g. #1 to #8)

    return {
        "asset_id": stop_data.get("asset_id"),
        "stop_name": stop_data.get("name"),
        "intervention_type": "shade_structure",
        "scenario": scenario,
        "scenario_description": cfg["description"],
        "effectiveness_factor": eff,
        "baseline_dangerous_minutes": baseline_dangerous_mins,
        "projected_dangerous_minutes": projected_dangerous_mins,
        "avoided_dangerous_minutes": avoided_dangerous_mins,
        "baseline_cumulative_exceedance": baseline_exceedance,
        "projected_cumulative_exceedance": projected_exceedance,
        "baseline_heat_score": baseline_heat_score,
        "projected_heat_score": projected_heat_score,
        "baseline_priority_score": baseline_priority_score,
        "projected_priority_score": projected_priority_score,
        "baseline_rank": baseline_rank,
        "projected_rank": projected_rank,
        "rank_change": rank_change,
        "confidence": 0.88,
        "assumptions": {
            "exposure_reduction_pct": int(eff * 100),
            "planning_assumption_only": True
        }
    }
