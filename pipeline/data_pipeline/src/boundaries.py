"""
Boundary management and spatial clipping for Hartford, CT.
"""

from pathlib import Path
import json
import geopandas as gpd
from shapely.geometry import shape

BOUNDARIES_DIR = Path("data/boundaries")

def load_hartford_boundary() -> gpd.GeoDataFrame:
    """Load Hartford GeoDataFrame in EPSG:4326."""
    geojson_path = BOUNDARIES_DIR / "hartford.geojson"
    if geojson_path.exists():
        gdf = gpd.read_file(geojson_path)
        return gdf.to_crs("EPSG:4326")
    
    geom_path = BOUNDARIES_DIR / "hartford_geometry.json"
    if geom_path.exists():
        with geom_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            geom = shape(data)
            gdf = gpd.GeoDataFrame([{"NAME": "Hartford", "geometry": geom}], crs="EPSG:4326")
            return gdf
            
    raise FileNotFoundError("Hartford boundary files not found in data/boundaries/")

def load_hartford_bbox() -> dict:
    bbox_path = BOUNDARIES_DIR / "hartford_bbox.json"
    if bbox_path.exists():
        with bbox_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    gdf = load_hartford_boundary()
    minx, miny, maxx, maxy = gdf.total_bounds
    return {"west": float(minx), "south": float(miny), "east": float(maxx), "north": float(maxy)}
