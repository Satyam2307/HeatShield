"""
Master Data Engineering and ML Analytics Pipeline for HeatShield: ShadeStop.
Outputs all required Parquet files, GeoJSON, demo JSON fixture, and quality manifests.
"""

from pathlib import Path
import json
import yaml
import pandas as pd
import geopandas as gpd

from src.boundaries import load_hartford_boundary
from src.transit import load_or_generate_bus_stops
from src.fortyguard import FortyGuardAdapter
from src.exposure import calculate_exposure_metrics
from src.satellite import estimate_satellite_shade
from src.census import estimate_census_vulnerability
from src.scoring import calculate_priority_scores
from src.ml_analytics import detect_persistence_anomalies, run_sensitivity_analysis
from src.quality import generate_quality_manifest

PROCESSED_DIR = Path("data/processed")
FIXTURES_DIR = Path("data/fixtures")
CONFIG_PATH = Path("data_pipeline/config/pipeline_config.yaml")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

def run():
    print("=== [Data Engineering Pipeline] HeatShield: ShadeStop (Hartford, CT) ===")

    # Load YAML Config
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    start_date = cfg["analysis"]["start_date"]
    end_date = cfg["analysis"]["end_date"]
    threshold = cfg["analysis"]["danger_threshold"]
    weights = cfg["scoring"]["weights"]

    # 1. Load Boundary
    hartford_gdf = load_hartford_boundary()
    print(f"[1/8] Hartford boundary loaded ({len(hartford_gdf)} feature).")

    # 2. Ingest Bus Stops
    stops_gdf = load_or_generate_bus_stops(hartford_gdf)
    print(f"[2/8] Processed {len(stops_gdf)} bus stops within Hartford boundary.")

    # 3. Calculate Exposure, Shade, & Vulnerability
    fg = FortyGuardAdapter()
    exposure_rows, shade_rows, vuln_rows, bus_stop_rows = [], [], [], []
    timeseries_dict = {}

    for _, row in stops_gdf.iterrows():
        aid = row["asset_id"]
        lat, lon = row["latitude"], row["longitude"]
        shelter = row["shelter_status"]

        # Time series observations
        obs = fg.get_time_series_observations(aid, lat, lon, danger_threshold=threshold)
        timeseries_dict[aid] = obs
        
        # Exposure Metrics
        exp_m = calculate_exposure_metrics(obs, danger_threshold=threshold)
        exp_m["asset_id"] = aid
        exposure_rows.append(exp_m)

        # Shade Metrics
        sat_m = estimate_satellite_shade(lat, lon, shelter)
        sat_m["asset_id"] = aid
        shade_rows.append(sat_m)

        # Vulnerability Metrics
        cen_m = estimate_census_vulnerability(lat, lon)
        cen_m["asset_id"] = aid
        vuln_rows.append(cen_m)

        # Bus Stop Attributes
        bus_stop_rows.append({
            "asset_id": aid,
            "external_stop_id": row["external_stop_id"],
            "name": row["name"],
            "corridor": row["corridor"],
            "latitude": lat,
            "longitude": lon,
            "route_count": row["route_count"],
            "routes": row["routes"],
            "ridership": row["ridership"],
            "shelter_status": shelter,
            "source": row["source"],
            "transit_value_type": row["transit_value_type"]
        })

    df_bus_stops = pd.DataFrame(bus_stop_rows)
    df_exposure = pd.DataFrame(exposure_rows)
    df_shade = pd.DataFrame(shade_rows)
    df_vuln = pd.DataFrame(vuln_rows)

    print(f"[3/8] Extracted stop-level metrics across FortyGuard, Satellite, and ACS Census.")

    # 4. Save Core Component Parquet Tables
    df_bus_stops.to_parquet(PROCESSED_DIR / "hartford_bus_stops.parquet", index=False)
    df_exposure.to_parquet(PROCESSED_DIR / "hartford_exposure_metrics.parquet", index=False)
    df_shade.to_parquet(PROCESSED_DIR / "hartford_shade_metrics.parquet", index=False)
    df_vuln.to_parquet(PROCESSED_DIR / "hartford_vulnerability_metrics.parquet", index=False)
    print(f"[4/8] Written core Parquet tables to {PROCESSED_DIR}/")

    # 5. Join & Priority Scoring
    df_merged = df_bus_stops.merge(df_exposure, on="asset_id").merge(df_shade, on="asset_id").merge(df_vuln, on="asset_id")
    df_scored = calculate_priority_scores(df_merged, weights=weights)

    # 6. Optional ML Modules (Anomaly Detection & Sensitivity Analysis)
    df_scored = detect_persistence_anomalies(df_scored)
    sensitivity = run_sensitivity_analysis(df_scored)
    print(f"[5/8] Priority scoring & ML anomaly detection complete. Sensitivity stability: {sensitivity['ranking_stability']}.")

    # Save Priority Scores Parquet
    df_scored.to_parquet(PROCESSED_DIR / "hartford_priority_scores.parquet", index=False)
    print(f"[6/8] Saved hartford_priority_scores.parquet")

    # 7. GeoJSON & Demo Fixture Generation
    features = []
    rankings_list = []

    for _, r in df_scored.iterrows():
        aid = r["asset_id"]
        obs = timeseries_dict[aid]

        feat = {
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["longitude"], r["latitude"]]},
            "properties": {
                "asset_id": aid,
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
                "is_heat_anomaly": bool(r["is_heat_anomaly"])
            }
        }
        features.append(feat)

        ranking_item = {
            "asset_id": aid,
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
                "transit_value_type": r["transit_value_type"]
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

    geojson_data = {"type": "FeatureCollection", "features": features}
    demo_fixture = {
        "analysis_id": "hartford-demo-2024-07-15",
        "city": {"name": "Hartford", "state": "CT"},
        "scenario": {"start": start_date, "end": end_date, "metric": "heat_index", "threshold": threshold, "threshold_unit": "F"},
        "weights": weights,
        "total_stops": len(rankings_list),
        "rankings": rankings_list
    }

    with (PROCESSED_DIR / "hartford_priority_scores.geojson").open("w", encoding="utf-8") as f:
        json.dump(geojson_data, f, indent=2)
    with (FIXTURES_DIR / "hartford_demo.json").open("w", encoding="utf-8") as f:
        json.dump(demo_fixture, f, indent=2)

    print(f"[7/8] Generated GeoJSON and Demo Fixture JSON.")

    # 8. Manifest
    generate_quality_manifest(
        total_stops=len(df_scored),
        valid_stops=len(df_scored),
        start_date=start_date,
        end_date=end_date,
        danger_threshold=threshold,
        output_files=[
            str(PROCESSED_DIR / "hartford_bus_stops.parquet"),
            str(PROCESSED_DIR / "hartford_exposure_metrics.parquet"),
            str(PROCESSED_DIR / "hartford_shade_metrics.parquet"),
            str(PROCESSED_DIR / "hartford_vulnerability_metrics.parquet"),
            str(PROCESSED_DIR / "hartford_priority_scores.parquet"),
            str(PROCESSED_DIR / "hartford_priority_scores.geojson"),
            str(FIXTURES_DIR / "hartford_demo.json")
        ]
    )
    print("=== [8/8] Data Pipeline Completed Successfully! ===")

if __name__ == "__main__":
    run()
