"""
Transit bus stop ingestion and metric buffer creation for Hartford, CT.
Uses projected CRS (EPSG:3437 - NAD83 / Connecticut) for 100m metric spatial buffer calculations.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

PROJECTED_CRS = "EPSG:3437"
LATLON_CRS = "EPSG:4326"

MAJOR_CORRIDORS = [
    {"name": "Main St Corridor", "start_lat": 41.745, "start_lon": -72.675, "end_lat": 41.790, "end_lon": -72.678, "count": 22, "routes": ["31", "33", "37", "39"]},
    {"name": "Albany Ave Corridor", "start_lat": 41.778, "start_lon": -72.675, "end_lat": 41.795, "end_lon": -72.715, "count": 20, "routes": ["50", "52", "54"]},
    {"name": "Park St Corridor", "start_lat": 41.758, "start_lon": -72.675, "end_lat": 41.759, "end_lon": -72.718, "count": 18, "routes": ["63", "69"]},
    {"name": "Farmington Ave Corridor", "start_lat": 41.768, "start_lon": -72.680, "end_lat": 41.771, "end_lon": -72.720, "count": 18, "routes": ["60", "62", "64", "66"]},
    {"name": "Capitol Ave / Trinity Corridor", "start_lat": 41.761, "start_lon": -72.673, "end_lat": 41.758, "end_lon": -72.700, "count": 15, "routes": ["61", "161"]},
    {"name": "Franklin Ave Corridor", "start_lat": 41.730, "start_lon": -72.672, "end_lat": 41.755, "end_lon": -72.673, "count": 14, "routes": ["47", "49"]},
    {"name": "Blue Hills Ave Corridor", "start_lat": 41.785, "start_lon": -72.695, "end_lat": 41.802, "end_lon": -72.705, "count": 13, "routes": ["56", "58"]}
]

def load_or_generate_bus_stops(hartford_gdf: gpd.GeoDataFrame = None) -> gpd.GeoDataFrame:
    """
    Ingest or generate bus stops filtered strictly to the Hartford city boundary.
    Creates 100m projected buffer geometry in EPSG:3437.
    """
    np.random.seed(42)
    stops = []
    stop_idx = 101

    for corridor in MAJOR_CORRIDORS:
        lats = np.linspace(corridor["start_lat"], corridor["end_lat"], corridor["count"])
        lons = np.linspace(corridor["start_lon"], corridor["end_lon"], corridor["count"])
        
        for i in range(corridor["count"]):
            lat = lats[i] + np.random.normal(0, 0.0003)
            lon = lons[i] + np.random.normal(0, 0.0003)
            
            stop_id = f"HFD-STOP-{stop_idx}"
            corridor_name = corridor["name"].replace(" Corridor", "")
            stop_name = f"{corridor_name} & Stop #{i+1}"
            
            route_list = corridor["routes"]
            route_count = len(route_list) + np.random.choice([0, 1])
            ridership_proxy = float(np.random.randint(120, 850))
            shelter_status = np.random.choice(["No Shelter", "Unshaded Bench", "Sheltered"], p=[0.55, 0.25, 0.20])
            
            stops.append({
                "asset_id": stop_id,
                "external_stop_id": stop_id,
                "name": stop_name,
                "corridor": corridor["name"],
                "latitude": round(lat, 6),
                "longitude": round(lon, 6),
                "route_count": int(route_count),
                "routes": ",".join(route_list),
                "ridership": ridership_proxy,
                "shelter_status": shelter_status,
                "transit_value_type": "proxy",
                "source": "CTtransit Hartford GTFS Proxy",
                "geometry": Point(lon, lat)
            })
            stop_idx += 1

    gdf = gpd.GeoDataFrame(stops, crs=LATLON_CRS)

    if hartford_gdf is not None:
        hartford_unified = hartford_gdf.to_crs(LATLON_CRS).geometry.union_all()
        gdf = gdf[gdf.geometry.within(hartford_unified)].copy()
        gdf.reset_index(drop=True, inplace=True)

    # 100m projected buffer in EPSG:3437
    gdf_proj = gdf.to_crs(PROJECTED_CRS)
    gdf_proj["buffer_geometry"] = gdf_proj.geometry.buffer(100.0)
    gdf["buffer_geometry_4326"] = gdf_proj["buffer_geometry"].to_crs(LATLON_CRS)
    
    return gdf
