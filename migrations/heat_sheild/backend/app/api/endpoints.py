"""
FastAPI REST API Router for HeatShield: ShadeStop.
"""

from fastapi import APIRouter, HTTPException, Response
from typing import Dict, Any, List

from ..schemas.models import (
    AnalysisCreateRequest, RankingsResponse, SimulationRequest, ExplanationRequest
)
from ..providers.fortyguard_adapter import fortyguard_service
from ..services.explanation import generate_stop_explanation
from ..services.report import generate_rankings_csv
from pipeline.src.simulator import simulate_stop_intervention
from pipeline.src.scoring import calculate_dataset_priority_scores
import pandas as pd

router = APIRouter()

@router.get("/cities")
def get_cities():
    """Returns list of supported cities."""
    return [{
        "id": "hartford-ct",
        "name": "Hartford",
        "state": "CT",
        "boundary_type": "Census MultiPolygon",
        "primary_asset": "bus_stops",
        "bbox": {
            "west": -72.7180,
            "south": 41.7236,
            "east": -72.6425,
            "north": 41.8075
        }
    }]

@router.post("/analysis")
def create_analysis(req: AnalysisCreateRequest):
    """Create or load analysis scenario with custom threshold & category weights."""
    fixture = fortyguard_service.load_demo_fixture()
    
    # If custom weights or threshold provided, re-score rankings
    w = req.weights.model_dump()
    rankings = fixture["rankings"]
    
    # Convert to DataFrame for re-scoring if weights differ from default
    df = pd.DataFrame([{
        "asset_id": item["asset_id"],
        "name": item["name"],
        "corridor": item["corridor"],
        "latitude": item["latitude"],
        "longitude": item["longitude"],
        "route_count": item["transit_details"]["route_count"],
        "ridership": item["transit_details"]["ridership"],
        "dangerous_minutes": item["metrics"]["dangerous_minutes"],
        "persistence_minutes": item["metrics"]["persistence_minutes"],
        "cumulative_exceedance": item["metrics"]["cumulative_exceedance"],
        "shade_deficit": item["shade_details"]["shade_deficit"],
        "raw_vulnerability_score": item["vulnerability_details"]["median_income"]  # proxy for rescore
    } for item in rankings])
    
    scored_df = calculate_dataset_priority_scores(df, weights=w)
    
    # Update rankings with new priority scores and ranks
    rank_map = {row["asset_id"]: (row["rank"], row["priority_score"], row["priority_category"]) for _, row in scored_df.iterrows()}
    
    updated_rankings = []
    for item in rankings:
        aid = item["asset_id"]
        if aid in rank_map:
            rk, ps, cat = rank_map[aid]
            item_copy = dict(item)
            item_copy["rank"] = int(rk)
            item_copy["priority_score"] = float(ps)
            item_copy["priority_category"] = cat
            updated_rankings.append(item_copy)
            
    updated_rankings.sort(key=lambda x: x["rank"])

    return {
        "analysis_id": f"hartford-analysis-th{int(req.danger_threshold)}",
        "city": {"name": "Hartford", "state": "CT"},
        "scenario": {
            "start": req.start_time,
            "end": req.end_time,
            "metric": req.heat_metric,
            "threshold": req.danger_threshold,
            "threshold_unit": req.heat_unit
        },
        "weights": w,
        "total_stops": len(updated_rankings),
        "rankings": updated_rankings
    }

@router.get("/analyses/{analysis_id}/rankings")
def get_rankings(analysis_id: str):
    """Get prioritized list of bus stops for an analysis."""
    fixture = fortyguard_service.load_demo_fixture()
    return fixture

@router.get("/analyses/{analysis_id}/map-data")
def get_map_data(analysis_id: str):
    """Get map GeoJSON for Hartford bus stops and priority categories."""
    geojson = fortyguard_service.load_map_geojson()
    return geojson

@router.get("/assets/{asset_id}")
def get_asset_detail(asset_id: str):
    """Get detailed metrics for a single bus stop."""
    fixture = fortyguard_service.load_demo_fixture()
    for item in fixture["rankings"]:
        if item["asset_id"] == asset_id:
            return item
    raise HTTPException(status_code=404, detail="Bus stop asset not found")

@router.get("/assets/{asset_id}/timeseries")
def get_asset_timeseries(asset_id: str):
    """Get heat index timeseries profile for a bus stop."""
    fixture = fortyguard_service.load_demo_fixture()
    for item in fixture["rankings"]:
        if item["asset_id"] == asset_id:
            return {
                "asset_id": asset_id,
                "name": item["name"],
                "timeseries": item.get("timeseries", [])
            }
    raise HTTPException(status_code=404, detail="Bus stop asset not found")

@router.post("/interventions/simulate")
def simulate_intervention(req: SimulationRequest):
    """Simulate shade structure intervention on a target bus stop."""
    fixture = fortyguard_service.load_demo_fixture()
    rankings = fixture["rankings"]
    
    target_stop = None
    for item in rankings:
        if item["asset_id"] == req.asset_id:
            target_stop = item
            break
            
    if not target_stop:
        raise HTTPException(status_code=404, detail=f"Asset ID {req.asset_id} not found")
        
    simulation_result = simulate_stop_intervention(
        stop_data=target_stop,
        all_stops=rankings,
        scenario=req.scenario
    )
    return simulation_result

@router.post("/explanations")
def get_explanation(req: ExplanationRequest):
    """Get structured natural language explanation for a ranked bus stop."""
    fixture = fortyguard_service.load_demo_fixture()
    for item in fixture["rankings"]:
        if item["asset_id"] == req.asset_id:
            return generate_stop_explanation(item)
    raise HTTPException(status_code=404, detail=f"Asset ID {req.asset_id} not found")

@router.get("/reports/{analysis_id}")
def export_report(analysis_id: str):
    """Export analysis ranking report as downloadable CSV."""
    fixture = fortyguard_service.load_demo_fixture()
    rankings = fixture["rankings"]
    csv_content = generate_rankings_csv(rankings)
    
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=hartford_shade_interventions_{analysis_id}.csv"}
    )
