"""
Master Data & Analytics Pipeline execution script for HeatShield: ShadeStop (Hartford, CT).
Ingests boundaries, generates bus stops, calculates FortyGuard heat metrics, Census vulnerability,
Satellite shade proxy, score rankings, and outputs GeoJSON + demo JSON fixtures.
"""

from pathlib import Path
import json
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, mapping

from src.boundaries import load_hartford_boundary, load_hartford_bbox
from src.transit import generate_hartford_bus_stops
from src.fortyguard import FortyGuardAdapter, calculate_stop_heat_metrics
from src.satellite import estimate_satellite_shade_metrics
from src.census import estimate_census_vulnerability
from src.scoring import calculate_dataset_priority_scores
from src.quality import generate_quality_manifest

PROCESSED_DIR = Path("data/processed")
FIXTURES_DIR = Path("data/fixtures")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

def run():
    print("=== Starting HeatShield: ShadeStop Data Pipeline for Hartford, CT ===")
    
    # 1. Load Boundary
    hartford_boundary = load_hartford_boundary()
    print(f"[1/6] Loaded Hartford boundary ({len(hartford_boundary)} feature).")
    
    # 2. Ingest / Generate Hartford Bus Stops
    stops_gdf = generate_hartford_bus_stops(hartford_boundary)
    print(f"[2/6] Processed {len(stops_gdf)} Hartford bus stops.")
    
    # 3. Calculate FortyGuard Heat Metrics, Satellite Shade Proxy, & Census Vulnerability
    fg_adapter = FortyGuardAdapter()
    rows = []
    timeseries_dict = {}
    
    for idx, row in stops_gdf.iterrows():
        stop_id = row["external_stop_id"]
        lat, lon = row["latitude"], row["longitude"]
        shelter = row["shelter_status"]
        
        # Heat observations (10 AM - 6 PM)
        obs = fg_adapter.get_time_series_observations(stop_id, lat, lon, start_hour=10, end_hour=18, danger_threshold=95.0)
        timeseries_dict[stop_id] = obs
        heat_m = calculate_stop_heat_metrics(obs, danger_threshold=95.0)
        
        # Satellite Shade proxy
        sat_m = estimate_satellite_shade_metrics(lat, lon, shelter)
        
        # Census vulnerability
        cen_m = estimate_census_vulnerability(lat, lon)
        
        combined_row = {
            "asset_id": stop_id,
            "name": row["name"],
            "corridor": row["corridor"],
            "latitude": lat,
            "longitude": lon,
            "route_count": row["route_count"],
            "routes": row["routes"],
            "ridership": row["ridership"],
            "shelter_status": shelter,
            "average_heat": heat_m["average_heat"],
            "maximum_heat": heat_m["maximum_heat"],
            "dangerous_minutes": heat_m["dangerous_minutes"],
            "dangerous_intervals": heat_m["dangerous_intervals"],
            "persistence_minutes": heat_m["persistence_minutes"],
            "cumulative_exceedance": heat_m["cumulative_exceedance"],
            "peak_hour": heat_m["peak_hour"],
            "vegetation_fraction": sat_m["vegetation_fraction"],
            "impervious_fraction": sat_m["impervious_fraction"],
            "building_fraction": sat_m["building_fraction"],
            "shade_deficit": sat_m["shade_deficit"],
            "geography_id": cen_m["geography_id"],
            "neighborhood_name": cen_m["neighborhood_name"],
            "median_income": cen_m["median_income"],
            "zero_vehicle_fraction": cen_m["zero_vehicle_fraction"],
            "older_adult_fraction": cen_m["older_adult_fraction"],
            "children_fraction": cen_m["children_fraction"],
            "population_density": cen_m["population_density"],
            "raw_vulnerability_score": cen_m["raw_vulnerability_score"]
        }
        rows.append(combined_row)
        
    df_raw = pd.DataFrame(rows)
    print(f"[3/6] Calculated heat, shade, and vulnerability metrics for {len(df_raw)} stops.")
    
    # 4. Score & Rank
    df_scored = calculate_dataset_priority_scores(df_raw)
    print(f"[4/6] Priority scoring completed. Top ranked stop: {df_scored.iloc[0]['name']} (Score: {df_scored.iloc[0]['priority_score']}).")
    
    # 5. Format GeoJSON & Demo Fixture JSON
    geojson_features = []
    rankings_list = []
    
    for _, r in df_scored.iterrows():
        stop_id = r["asset_id"]
        obs = timeseries_dict[stop_id]
        
        feature_item = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [r["longitude"], r["latitude"]]
            },
            "properties": {
                "asset_id": r["asset_id"],
                "name": r["name"],
                "corridor": r["corridor"],
                "rank": int(r["rank"]),
                "priority_score": float(r["priority_score"]),
                "priority_category": r["priority_category"],
                "heat_score": float(r["heat_score"]),
                "shade_score": float(r["shade_score"]),
                "vulnerability_score": float(r["vulnerability_score"]),
                "transit_score": float(r["transit_score"]),
                "dangerous_minutes": float(r["dangerous_minutes"]),
                "persistence_minutes": float(r["persistence_minutes"]),
                "cumulative_exceedance": float(r["cumulative_exceedance"]),
                "peak_hour": int(r["peak_hour"]),
                "shelter_status": r["shelter_status"],
                "vegetation_fraction": float(r["vegetation_fraction"]),
                "shade_deficit": float(r["shade_deficit"]),
                "zero_vehicle_fraction": float(r["zero_vehicle_fraction"]),
                "neighborhood_name": r["neighborhood_name"]
            }
        }
        geojson_features.append(feature_item)
        
        ranking_item = {
            "asset_id": r["asset_id"],
            "rank": int(r["rank"]),
            "name": r["name"],
            "corridor": r["corridor"],
            "latitude": float(r["latitude"]),
            "longitude": float(r["longitude"]),
            "priority_score": float(r["priority_score"]),
            "priority_category": r["priority_category"],
            "components": {
                "heat": float(r["heat_score"]),
                "shade": float(r["shade_score"]),
                "vulnerability": float(r["vulnerability_score"]),
                "transit": float(r["transit_score"])
            },
            "metrics": {
                "average_heat": float(r["average_heat"]),
                "maximum_heat": float(r["maximum_heat"]),
                "dangerous_minutes": float(r["dangerous_minutes"]),
                "dangerous_intervals": int(r["dangerous_intervals"]),
                "persistence_minutes": float(r["persistence_minutes"]),
                "cumulative_exceedance": float(r["cumulative_exceedance"]),
                "peak_hour": int(r["peak_hour"])
            },
            "shade_details": {
                "vegetation_fraction": float(r["vegetation_fraction"]),
                "impervious_fraction": float(r["impervious_fraction"]),
                "building_fraction": float(r["building_fraction"]),
                "shade_deficit": float(r["shade_deficit"]),
                "shelter_status": r["shelter_status"]
            },
            "vulnerability_details": {
                "geography_id": r["geography_id"],
                "neighborhood_name": r["neighborhood_name"],
                "median_income": float(r["median_income"]),
                "zero_vehicle_fraction": float(r["zero_vehicle_fraction"]),
                "older_adult_fraction": float(r["older_adult_fraction"]),
                "children_fraction": float(r["children_fraction"]),
                "population_density": float(r["population_density"])
            },
            "transit_details": {
                "route_count": int(r["route_count"]),
                "routes": r["routes"].split(","),
                "ridership": float(r["ridership"]),
                "transit_value_type": "proxy"
            },
            "metadata": {
                "shade_is_proxy": True,
                "transit_is_proxy": True,
                "data_coverage": 1.0,
                "confidence": 0.89
            },
            "timeseries": obs
        }
        rankings_list.append(ranking_item)
        
    geojson_data = {
        "type": "FeatureCollection",
        "name": "Hartford Bus Stops Prioritization",
        "features": geojson_features
    }
    
    demo_fixture_data = {
        "analysis_id": "hartford-demo-2024-07-15",
        "city": {"name": "Hartford", "state": "CT"},
        "scenario": {
            "start": "2024-07-15T10:00:00-04:00",
            "end": "2024-07-15T18:00:00-04:00",
            "metric": "heat_index",
            "threshold": 95.0,
            "threshold_unit": "F"
        },
        "weights": {"heat": 0.40, "shade": 0.25, "vulnerability": 0.20, "transit": 0.15},
        "total_stops": len(rankings_list),
        "rankings": rankings_list
    }
    
    # Write GeoJSON file
    geojson_out = PROCESSED_DIR / "hartford_priority_scores.geojson"
    with geojson_out.open("w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)
    print(f"[5/6] Saved GeoJSON output: {geojson_out}")
    
    # Write Demo Fixture file
    fixture_out = FIXTURES_DIR / "hartford_demo.json"
    with fixture_out.open("w", encoding="utf-8") as f:
        json.dump(demo_fixture_data, f, indent=2)
    print(f"[5/6] Saved Demo Fixture JSON output: {fixture_out}")
    
    # 6. Quality Manifest
    generate_quality_manifest(
        total_stops=len(df_scored),
        valid_stops=len(df_scored),
        start_date="2024-07-15T10:00:00-04:00",
        end_date="2024-07-15T18:00:00-04:00",
        danger_threshold=95.0,
        output_files=[str(geojson_out), str(fixture_out)]
    )
    print("=== Data Pipeline Execution Finished Successfully! ===")

if __name__ == "__main__":
    run()
