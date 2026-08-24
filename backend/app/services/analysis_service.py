"""
Analysis service — orchestrates a complete bus-stop heat analysis.

This is the core business logic that:
1. Loads boundary and stops
2. Computes heat exposure per stop
3. Calculates shade, vulnerability, and transit scores
4. Normalizes and ranks all stops
5. Returns a complete analysis result
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.config import settings, PROCESSED_DIR
from app.services import fixture_service
from app.scoring.exceedance import (
    calculate_cumulative_exceedance,
    calculate_dangerous_minutes,
    calculate_dangerous_intervals,
)
from app.scoring.persistence import calculate_persistence
from app.scoring.heat_score import calculate_heat_scores
from app.scoring.shade_score import calculate_shade_deficit, calculate_shade_scores
from app.scoring.vulnerability_score import calculate_vulnerability_scores
from app.scoring.transit_score import calculate_transit_score, percentile_normalize_transit
from app.scoring.priority import calculate_priority_scores


# ---------------------------------------------------------------------------
# In-memory store for completed analyses (hackathon simplicity)
# ---------------------------------------------------------------------------
_analyses: dict[str, dict] = {}


def run_analysis(
    analysis_id: str = "fixture-001",
    city_id: str = "hartford-ct",
    start_time: str | None = None,
    end_time: str | None = None,
    heat_metric: str = "heat_index",
    heat_unit: str = "F",
    danger_threshold: float = 95.0,
    interval_minutes: int = 60,
    buffer_meters: int = 100,
    weights: dict[str, float] | None = None,
) -> dict:
    """
    Run a complete heat-intervention priority analysis.

    Returns:
        Analysis result dict with all stop scores and rankings.
    """
    # Check cache first
    if analysis_id in _analyses:
        return _analyses[analysis_id]

    # 1. Load data
    stops_geojson = fixture_service.load_bus_stops()
    heat_data = fixture_service.load_heat_observations()
    shade_data = fixture_service.load_shade_metrics()
    vuln_data = fixture_service.load_vulnerability()

    features = stops_geojson["features"]
    n = len(features)

    # 2. Calculate exposure metrics per stop
    cumulative_exceedances = []
    dangerous_minutes_list = []
    persistence_minutes_list = []
    stop_exposure: dict[str, dict] = {}

    for feature in features:
        stop_id = feature["properties"]["id"]
        observations = heat_data.get(stop_id, [])

        values = [obs["value"] for obs in observations]
        timestamps = [obs["timestamp"] for obs in observations]

        # Exceedance
        cum_exc = calculate_cumulative_exceedance(values, danger_threshold, interval_minutes)
        dang_min = calculate_dangerous_minutes(values, danger_threshold, interval_minutes)
        dang_int = calculate_dangerous_intervals(values, danger_threshold)

        # Persistence
        pers = calculate_persistence(values, timestamps, danger_threshold, interval_minutes)

        # Peak hour
        peak_hour = None
        peak_value = None
        if values:
            max_idx = values.index(max(values))
            peak_value = values[max_idx]
            # Extract hour from timestamp
            try:
                ts = timestamps[max_idx]
                # Parse ISO timestamp to get hour
                if "T" in ts:
                    time_part = ts.split("T")[1]
                    peak_hour = int(time_part.split(":")[0])
            except (IndexError, ValueError):
                pass

        avg_heat = sum(values) / len(values) if values else None
        max_heat = max(values) if values else None

        cumulative_exceedances.append(cum_exc)
        dangerous_minutes_list.append(dang_min)
        persistence_minutes_list.append(pers.persistence_minutes)

        stop_exposure[stop_id] = {
            "average_heat": round(avg_heat, 1) if avg_heat else None,
            "maximum_heat": round(max_heat, 1) if max_heat else None,
            "dangerous_minutes": dang_min,
            "dangerous_intervals": dang_int,
            "persistence_minutes": pers.persistence_minutes,
            "persistence_start": pers.persistence_start,
            "persistence_end": pers.persistence_end,
            "cumulative_exceedance": cum_exc,
            "peak_hour": peak_hour,
            "peak_value": peak_value,
            "data_coverage": 1.0 if values else 0.0,
        }

    # 3. Calculate heat scores (percentile-normalized)
    heat_results = calculate_heat_scores(
        cumulative_exceedances,
        dangerous_minutes_list,
        persistence_minutes_list,
    )
    heat_scores = [r["heat_score"] for r in heat_results]

    # 4. Calculate shade scores
    shade_deficits = []
    for feature in features:
        stop_id = feature["properties"]["id"]
        sm = shade_data.get(stop_id, {})
        deficit = calculate_shade_deficit(
            vegetation_fraction=sm.get("vegetation_fraction"),
            impervious_fraction=sm.get("impervious_fraction"),
            building_fraction=sm.get("building_fraction"),
            canopy_fraction=sm.get("canopy_fraction"),
            shelter_status=sm.get("shelter_status"),
        )
        shade_deficits.append(deficit)
    shade_scores = calculate_shade_scores(shade_deficits)

    # 5. Calculate vulnerability scores
    vuln_indicators = []
    for feature in features:
        stop_id = feature["properties"]["id"]
        vi = vuln_data.get(stop_id, {})
        vuln_indicators.append(vi)
    vulnerability_scores = calculate_vulnerability_scores(vuln_indicators)

    # 6. Calculate transit scores
    transit_raw = []
    transit_types = []
    for feature in features:
        props = feature["properties"]
        score, dtype = calculate_transit_score(
            route_count=props.get("route_count"),
            ridership=props.get("ridership"),
        )
        transit_raw.append(score)
        transit_types.append(dtype)
    transit_scores = percentile_normalize_transit(transit_raw)

    # 7. Calculate priority scores and rankings
    priority_results = calculate_priority_scores(
        heat_scores=heat_scores,
        shade_scores=shade_scores,
        vulnerability_scores=vulnerability_scores,
        transit_scores=transit_scores,
        weights=weights,
    )

    # 8. Build final result
    stops_result = []
    for i, feature in enumerate(features):
        stop_id = feature["properties"]["id"]
        props = feature["properties"]
        coords = feature["geometry"]["coordinates"]

        stops_result.append({
            "id": stop_id,
            "external_stop_id": props.get("external_stop_id", ""),
            "name": props.get("name"),
            "latitude": coords[1],
            "longitude": coords[0],
            "route_count": props.get("route_count"),
            "shelter_status": props.get("shelter_status"),
            "source": props.get("source", "fixture"),

            # Exposure
            **stop_exposure[stop_id],

            # Component scores
            "heat_score": heat_results[i]["heat_score"],
            "cumulative_exceedance_percentile": heat_results[i]["cumulative_exceedance_percentile"],
            "dangerous_minutes_percentile": heat_results[i]["dangerous_minutes_percentile"],
            "persistence_percentile": heat_results[i]["persistence_percentile"],
            "shade_score": shade_scores[i],
            "shade_deficit": shade_deficits[i],
            "vulnerability_score": vulnerability_scores[i],
            "transit_score": transit_scores[i],
            "transit_data_type": transit_types[i],

            # Priority
            "priority_score": priority_results[i]["final_score"],
            "rank": priority_results[i]["rank"],
            "priority_category": priority_results[i]["priority_category"],
            "scoring_version": priority_results[i]["scoring_version"],

            # Shade metrics detail
            "shade_metrics": shade_data.get(stop_id, {}),
            # Vulnerability detail
            "vulnerability_metrics": vuln_data.get(stop_id, {}),
        })

    analysis_result = {
        "analysis_id": analysis_id,
        "city_id": city_id,
        "status": "completed",
        "start_time": start_time or f"{settings.default_analysis_date}T{settings.default_start_hour:02d}:00:00-04:00",
        "end_time": end_time or f"{settings.default_analysis_date}T{settings.default_end_hour:02d}:00:00-04:00",
        "heat_metric": heat_metric,
        "heat_unit": heat_unit,
        "danger_threshold": danger_threshold,
        "interval_minutes": interval_minutes,
        "buffer_meters": buffer_meters,
        "scoring_version": settings.scoring_version,
        "total_stops": n,
        "weights": weights or {
            "heat": settings.scoring_weights.heat,
            "shade": settings.scoring_weights.shade,
            "vulnerability": settings.scoring_weights.vulnerability,
            "transit": settings.scoring_weights.transit,
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "stops": sorted(stops_result, key=lambda s: s["rank"]),
    }

    # Cache in memory
    _analyses[analysis_id] = analysis_result

    return analysis_result


def get_analysis(analysis_id: str) -> dict | None:
    """Retrieve a completed analysis by ID."""
    if analysis_id not in _analyses:
        # Auto-run fixture analysis for any ID (e.g. analysis-001, fixture-001, etc.)
        return run_analysis(analysis_id=analysis_id)
    return _analyses.get(analysis_id)


def export_priority_geojson(analysis_id: str = "fixture-001") -> dict:
    """
    Export analysis as a GeoJSON FeatureCollection.

    This produces the MVP deliverable: hartford_priority_scores.geojson
    """
    analysis = get_analysis(analysis_id)
    if not analysis:
        analysis = run_analysis(analysis_id=analysis_id)

    features = []
    for stop in analysis["stops"]:
        features.append({
            "type": "Feature",
            "properties": {
                "stop_id": stop["id"],
                "stop_name": stop.get("name"),
                "external_stop_id": stop["external_stop_id"],
                "heat_score": stop["heat_score"],
                "shade_score": stop["shade_score"],
                "vulnerability_score": stop["vulnerability_score"],
                "transit_score": stop["transit_score"],
                "priority_score": stop["priority_score"],
                "rank": stop["rank"],
                "priority_category": stop["priority_category"],
                "dangerous_minutes": stop["dangerous_minutes"],
                "persistence_minutes": stop["persistence_minutes"],
                "cumulative_exceedance": stop["cumulative_exceedance"],
                "peak_hour": stop.get("peak_hour"),
                "average_heat": stop.get("average_heat"),
                "maximum_heat": stop.get("maximum_heat"),
                "shade_deficit": stop.get("shade_deficit"),
                "route_count": stop.get("route_count"),
                "shelter_status": stop.get("shelter_status"),
                "scoring_version": stop.get("scoring_version"),
            },
            "geometry": {
                "type": "Point",
                "coordinates": [stop["longitude"], stop["latitude"]],
            },
        })

    return {
        "type": "FeatureCollection",
        "metadata": {
            "analysis_id": analysis["analysis_id"],
            "city": analysis["city_id"],
            "analysis_date": analysis["start_time"].split("T")[0],
            "heat_metric": analysis["heat_metric"],
            "danger_threshold": analysis["danger_threshold"],
            "scoring_version": analysis["scoring_version"],
            "total_stops": analysis["total_stops"],
        },
        "features": features,
    }


def save_priority_geojson(analysis_id: str = "fixture-001") -> Path:
    """Generate and save the MVP GeoJSON deliverable."""
    geojson = export_priority_geojson(analysis_id)
    output_path = PROCESSED_DIR / "hartford_priority_scores.geojson"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(geojson, f, indent=2)
    return output_path
