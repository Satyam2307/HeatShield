"""
Comprehensive Pytest suite for HeatShield data pipeline.
"""

import pytest
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point

from data_pipeline.src.boundaries import load_hartford_boundary
from data_pipeline.src.transit import load_or_generate_bus_stops
from data_pipeline.src.exposure import calculate_exposure_metrics
from data_pipeline.src.scoring import to_percentile_ranks, calculate_priority_scores
from data_pipeline.src.ml_analytics import detect_persistence_anomalies, run_sensitivity_analysis
from data_pipeline.src.quality import generate_quality_manifest

def test_boundary_loading():
    gdf = load_hartford_boundary()
    assert isinstance(gdf, gpd.GeoDataFrame)
    assert gdf.crs.to_string() == "EPSG:4326"
    assert len(gdf) >= 1

def test_bus_stop_filtering_and_projected_buffer():
    hartford = load_hartford_boundary()
    stops = load_or_generate_bus_stops(hartford)
    assert len(stops) > 50
    assert "buffer_geometry_4326" in stops.columns
    # Confirm longitude/latitude are strictly within Hartford extent
    minx, miny, maxx, maxy = hartford.total_bounds
    for _, stop in stops.iterrows():
        assert minx - 0.05 <= stop.longitude <= maxx + 0.05
        assert miny - 0.05 <= stop.latitude <= maxy + 0.05

def test_exceedance_and_persistence_metrics():
    obs = [
        {"hour": 10, "heat_index": 92.0},
        {"hour": 11, "heat_index": 94.0},
        {"hour": 12, "heat_index": 96.0}, # +1
        {"hour": 13, "heat_index": 98.0}, # +3
        {"hour": 14, "heat_index": 97.0}, # +2
        {"hour": 15, "heat_index": 91.0},
        {"hour": 16, "heat_index": 90.0}
    ]
    res = calculate_exposure_metrics(obs, danger_threshold=95.0)
    assert res["cumulative_exceedance"] == 6.0
    assert res["dangerous_intervals"] == 3
    assert res["dangerous_minutes"] == 180.0
    assert res["persistence_minutes"] == 180.0
    assert res["peak_hour"] == 13

def test_percentile_scoring_and_categories():
    df = pd.DataFrame([
        {"asset_id": "s1", "cumulative_exceedance": 10.0, "dangerous_minutes": 240.0, "persistence_minutes": 180.0, "shade_deficit": 0.85, "raw_vulnerability_score": 75.0, "ridership": 500, "route_count": 4},
        {"asset_id": "s2", "cumulative_exceedance": 2.0, "dangerous_minutes": 60.0, "persistence_minutes": 60.0, "shade_deficit": 0.40, "raw_vulnerability_score": 30.0, "ridership": 100, "route_count": 1}
    ])
    scored = calculate_priority_scores(df)
    assert len(scored) == 2
    assert scored.iloc[0]["priority_score"] > scored.iloc[1]["priority_score"]
    assert scored.iloc[0]["priority_category"] in ["Critical", "High"]

def test_ml_anomaly_and_sensitivity():
    df = pd.DataFrame([
        {"asset_id": "s1", "corridor": "Main St", "persistence_minutes": 240.0, "cumulative_exceedance": 15.0, "dangerous_minutes": 240.0, "shade_deficit": 0.90, "raw_vulnerability_score": 80.0, "ridership": 600, "route_count": 4},
        {"asset_id": "s2", "corridor": "Main St", "persistence_minutes": 60.0, "cumulative_exceedance": 2.0, "dangerous_minutes": 60.0, "shade_deficit": 0.40, "raw_vulnerability_score": 30.0, "ridership": 100, "route_count": 1},
        {"asset_id": "s3", "corridor": "Main St", "persistence_minutes": 50.0, "cumulative_exceedance": 1.0, "dangerous_minutes": 50.0, "shade_deficit": 0.30, "raw_vulnerability_score": 20.0, "ridership": 80, "route_count": 1}
    ])
    anom = detect_persistence_anomalies(df)
    assert "is_heat_anomaly" in anom.columns
    assert anom.iloc[0]["is_heat_anomaly"] == True

    sens = run_sensitivity_analysis(df)
    assert "ranking_stability" in sens

def test_manifest_generation():
    m = generate_quality_manifest(100, 100, "2024-07-15T10:00:00-04:00", "2024-07-15T18:00:00-04:00", 95.0, ["test.parquet"], manifest_dir="data_pipeline/manifests")
    assert m["city"] == "Hartford"
    assert m["total_stops"] == 100
