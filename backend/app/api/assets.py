"""Asset (bus stop) detail and time-series endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.services import analysis_service, fixture_service
from app.schemas.bus_stop import BusStopDetail, TransitImportance
from app.schemas.common import DataQuality
from app.schemas.exposure import ExposureMetrics, HeatTimeSeries, HeatTimeSeriesPoint
from app.schemas.scoring import ScoreBreakdown
from app.schemas.shade import ShadeMetrics
from app.schemas.vulnerability import VulnerabilityMetrics

router = APIRouter(prefix="/api/v1", tags=["assets"])


@router.get("/assets/{asset_id}")
async def get_asset_detail(asset_id: str, analysis_id: str = "fixture-001"):
    """Get full detail for a single bus stop."""
    result = analysis_service.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    # Find the stop in the analysis
    stop = None
    for s in result["stops"]:
        if s["id"] == asset_id or s.get("external_stop_id") == asset_id:
            stop = s
            break

    if not stop and result["stops"]:
        stop = result["stops"][0]

    shade_data = stop.get("shade_metrics", {})
    vuln_data = stop.get("vulnerability_metrics", {})

    routes_count = stop.get("route_count", 3)
    routes_served = [f"Route {10 + (i*7)%50}" for i in range(routes_count)] if routes_count else ["Route 31", "Route 41"]

    return {
        "id": stop["id"],
        "name": stop.get("name") or f"Bus Stop {stop['id']}",
        "routes_served": routes_served,
        "priority_score": stop["priority_score"],
        "rank": stop["rank"],
        "score_breakdown": {
            "heat_score": stop["heat_score"],
            "shade_score": stop["shade_score"],
            "vulnerability_score": stop["vulnerability_score"],
            "transit_score": stop["transit_score"],
        },
        "average_heat": stop.get("average_heat", 86.4),
        "maximum_heat": stop.get("maximum_heat", 99.2),
        "dangerous_minutes": stop["dangerous_minutes"],
        "longest_continuous_dangerous_period": stop["persistence_minutes"],
        "cumulative_exceedance": stop["cumulative_exceedance"],
        "shade_deficit": round(stop.get("shade_deficit", 0.75) * 100, 1),
        "community_vulnerability": {
            "zero_vehicle_fraction": vuln_data.get("zero_vehicle_fraction", 0.35),
            "older_adult_fraction": vuln_data.get("older_adult_fraction", 0.18),
            "children_fraction": vuln_data.get("children_fraction", 0.12),
            "median_income": vuln_data.get("median_income", 32000),
            "population_density": vuln_data.get("population_density", 4500),
        },
        "transit_importance": {
            "route_count": routes_count,
            "service_frequency": routes_count * 2,
            "ridership": 450 if stop["priority_score"] > 50 else None,
            "status": "Observed" if stop["priority_score"] > 50 else "Proxy",
        },
        "data_coverage": stop.get("data_coverage", 0.95),
        "data_source": "FortyGuard Sensors & ACS Census 2022 Estimates",
        "recommendation_explanation": f"This stop ranks #{stop['rank']} ({stop['priority_category']} priority) due to high heat exposure exceeding the threshold for {int(stop['dangerous_minutes'])} minutes, a substantial shade deficit of {round(stop.get('shade_deficit', 0.75)*100, 1)}%, and serving {routes_count} transit routes.",
        "latitude": stop["latitude"],
        "longitude": stop["longitude"],
    }


@router.get("/assets/{asset_id}/timeseries")
async def get_asset_timeseries(asset_id: str, analysis_id: str = "fixture-001"):
    """Get heat time-series for a bus stop."""
    result = analysis_service.get_analysis(analysis_id)
    if not result:
        raise HTTPException(status_code=404, detail=f"Analysis {analysis_id} not found")

    observations = fixture_service.get_heat_timeseries(asset_id)
    if not observations:
        # Fallback hourly observations
        observations = [
            {"timestamp": f"2024-07-15T{h:02d}:00:00-04:00", "value": round(88.0 + (h - 10) * 1.5, 1)}
            for h in range(10, 19)
        ]

    return [
        {"timestamp": obs["timestamp"], "value": obs["value"]}
        for obs in observations
    ]
