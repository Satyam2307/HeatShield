"""Intervention simulation endpoint."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services import analysis_service
from app.scoring.intervention import simulate_shade_intervention
from app.schemas.intervention import InterventionRequest, InterventionResult, InterventionAssumptions

router = APIRouter(prefix="/api/v1", tags=["interventions"])


@router.post("/interventions/simulate")
async def simulate_intervention(request: InterventionRequest):
    """
    Simulate the impact of a shade structure on a bus stop.

    Returns baseline vs. projected metrics and rank change.
    """
    result = analysis_service.get_analysis(request.analysis_id)
    if not result:
        result = analysis_service.run_analysis(analysis_id="fixture-001")

    # Find the stop
    stop = None
    for s in result["stops"]:
        if s["id"] == request.asset_id or s.get("external_stop_id") == request.asset_id:
            stop = s
            break

    if not stop and result["stops"]:
        stop = result["stops"][0]

    # Get all priority scores for re-ranking
    all_scores = [s["priority_score"] for s in result["stops"] if s["id"] != stop["id"]]

    sim = simulate_shade_intervention(
        baseline_dangerous_minutes=stop["dangerous_minutes"],
        baseline_cumulative_exceedance=stop["cumulative_exceedance"],
        baseline_heat_score=stop["heat_score"],
        baseline_priority_score=stop["priority_score"],
        baseline_rank=stop["rank"],
        all_baseline_priority_scores=all_scores,
        scenario=request.scenario,
        shade_score=stop["shade_score"],
        vulnerability_score=stop["vulnerability_score"],
        transit_score=stop["transit_score"],
    )

    return {
        "baseline_dangerous_minutes": sim["baseline_dangerous_minutes"],
        "projected_dangerous_minutes": sim["projected_dangerous_minutes"],
        "avoided_dangerous_minutes": sim["avoided_dangerous_minutes"],
        "exposure_reduction_pct": sim["percentage_reduction"],
        "baseline_priority_score": sim["baseline_priority_score"],
        "projected_priority_score": sim["projected_priority_score"],
        "rank_change": sim["rank_change"],
        "assumptions": f"Based on a mathematical projection where the {request.scenario} shade structure scenario reduces direct thermal exposure by {sim['percentage_reduction']}%. This is a planning scenario, not a final engineering estimate.",
        # Backwards compat keys:
        "percentage_reduction": sim["percentage_reduction"],
        "analysis_id": request.analysis_id,
        "asset_id": request.asset_id,
    }
