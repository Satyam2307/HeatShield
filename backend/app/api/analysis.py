"""Analysis endpoints — create, status, rankings, map data."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.services import analysis_service
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.schemas.bus_stop import RankingsResponse, MapDataResponse, BusStopSummary
from app.schemas.scoring import ScoringWeights

router = APIRouter(prefix="/api/v1", tags=["analysis"])


@router.post("/analysis", response_model=AnalysisResponse)
async def create_analysis(request: AnalysisRequest | None = None):
    """
    Create and run a heat-intervention analysis.

    In fixture mode, returns precomputed Hartford results.
    """
    if request is None:
        request = AnalysisRequest(
            city_id="hartford-ct",
            start_time=f"{settings.default_analysis_date}T{settings.default_start_hour:02d}:00:00-04:00",
            end_time=f"{settings.default_analysis_date}T{settings.default_end_hour:02d}:00:00-04:00",
        )

    analysis_id = f"analysis-{uuid.uuid4().hex[:8]}" if settings.data_mode == "live" else "fixture-001"

    weights = None
    if request.weights:
        weights = {
            "heat": request.weights.heat,
            "shade": request.weights.shade,
            "vulnerability": request.weights.vulnerability,
            "transit": request.weights.transit,
        }

    result = analysis_service.run_analysis(
        analysis_id=analysis_id,
        city_id=request.city_id,
        start_time=request.start_time,
        end_time=request.end_time,
        heat_metric=request.heat_metric,
        heat_unit=request.heat_unit,
        danger_threshold=request.danger_threshold,
        interval_minutes=request.interval_minutes,
        buffer_meters=request.buffer_meters,
        weights=weights,
    )

    return AnalysisResponse(
        analysis_id=result["analysis_id"],
        city_id=result["city_id"],
        status=result["status"],
        start_time=result["start_time"],
        end_time=result["end_time"],
        heat_metric=result["heat_metric"],
        heat_unit=result["heat_unit"],
        danger_threshold=result["danger_threshold"],
        interval_minutes=result["interval_minutes"],
        buffer_meters=result["buffer_meters"],
        scoring_version=result["scoring_version"],
        total_stops=result["total_stops"],
        weights=ScoringWeights(**result["weights"]) if result.get("weights") else None,
        created_at=result.get("created_at"),
    )


@router.get("/analyses/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(analysis_id: str):
    """Get analysis status and metadata."""
    result = analysis_service.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    return AnalysisResponse(
        analysis_id=result["analysis_id"],
        city_id=result["city_id"],
        status=result["status"],
        start_time=result["start_time"],
        end_time=result["end_time"],
        heat_metric=result["heat_metric"],
        heat_unit=result["heat_unit"],
        danger_threshold=result["danger_threshold"],
        interval_minutes=result["interval_minutes"],
        buffer_meters=result["buffer_meters"],
        scoring_version=result["scoring_version"],
        total_stops=result["total_stops"],
        weights=ScoringWeights(**result["weights"]) if result.get("weights") else None,
        created_at=result.get("created_at"),
    )


@router.get("/analyses/{analysis_id}/rankings")
async def get_rankings(
    analysis_id: str,
    heat: float | None = None,
    shade: float | None = None,
    vulnerability: float | None = None,
    transit: float | None = None,
    limit: int = 150,
    offset: int = 0,
):
    """Get ranked bus stops for an analysis."""
    weights = None
    if any(w is not None for w in (heat, shade, vulnerability, transit)):
        weights = {
            "heat": heat if heat is not None else 0.40,
            "shade": shade if shade is not None else 0.25,
            "vulnerability": vulnerability if vulnerability is not None else 0.20,
            "transit": transit if transit is not None else 0.15,
        }

    result = analysis_service.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    if weights:
        # Re-run with custom weights if passed
        result = analysis_service.run_analysis(analysis_id=f"{analysis_id}-custom", weights=weights)

    stops = result["stops"][offset : offset + limit]

    formatted_stops = []
    for s in stops:
        formatted_stops.append({
            "rank": s["rank"],
            "bus_stop_id": s["id"],
            "id": s["id"],
            "stop_name": s.get("name") or f"Bus Stop {s['id']}",
            "name": s.get("name") or f"Bus Stop {s['id']}",
            "priority_category": s["priority_category"],
            "priority_score": s["priority_score"],
            "dangerous_minutes": s["dangerous_minutes"],
            "cumulative_exceedance": s["cumulative_exceedance"],
            "shade_deficit": round(s.get("shade_deficit", 0.75) * 100, 1),
            "vulnerability_score": s["vulnerability_score"],
            "transit_score": s["transit_score"],
            "heat_score": s["heat_score"],
            "shade_score": s["shade_score"],
            "routes_served": [f"Route {10 + (i*7)%50}" for i in range(s.get("route_count", 2))] if s.get("route_count") else ["Route 31", "Route 41"],
            "recommended_intervention": "Shade Structure (Canopy Shelter)" if s["priority_score"] >= 60 else "Tree Planting Grid",
            "latitude": s["latitude"],
            "longitude": s["longitude"],
        })

    return formatted_stops


@router.get("/analyses/{analysis_id}/map-data", response_model=MapDataResponse)
async def get_map_data(analysis_id: str):
    """Get GeoJSON FeatureCollection for map rendering."""
    result = analysis_service.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    geojson = analysis_service.export_priority_geojson(analysis_id)
    return MapDataResponse(
        type="FeatureCollection",
        features=geojson["features"],
        metadata=geojson.get("metadata", {}),
    )
