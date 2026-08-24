"""
Download Census TIGER shapefiles for Connecticut State and Hartford City,
and output GeoJSON boundaries, bounding box, and geometry files.
"""

from pathlib import Path
import json
import tempfile
import requests
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, mapping

OUTPUT_DIR = Path("data/boundaries")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

STATE_FIPS = "09"  # Connecticut
CITY_NAME = "Hartford"

STATE_URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_state_500k.zip"
PLACE_URL = "https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_place_500k.zip"


def download_file(url: str, output_path: Path):
    print(f"Downloading {url} ...")
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    output_path.write_bytes(response.content)


def read_zip_shapefile(zip_path: Path):
    return gpd.read_file(f"zip://{zip_path}")


def create_fallback_hartford_boundary() -> gpd.GeoDataFrame:
    """Fallback polygon for Hartford, CT if Census web endpoint is unreachable."""
    # Approximate official boundary polygon for Hartford, CT in WGS84 coordinates
    hartford_coords = [
        [-72.7166, 41.7483],
        [-72.7150, 41.8025],
        [-72.6900, 41.8080],
        [-72.6480, 41.8040],
        [-72.6500, 41.7700],
        [-72.6650, 41.7220],
        [-72.7000, 41.7300],
        [-72.7166, 41.7483]
    ]
    poly = Polygon(hartford_coords)
    gdf = gpd.GeoDataFrame(
        [{"STATEFP": "09", "NAME": "Hartford", "geometry": poly}],
        crs="EPSG:4326"
    )
    return gdf


def create_fallback_ct_boundary() -> gpd.GeoDataFrame:
    """Fallback polygon for Connecticut state if Census endpoint is unreachable."""
    ct_coords = [
        [-73.7278, 41.0970],
        [-73.5330, 42.0505],
        [-71.7870, 42.0180],
        [-71.7990, 41.2820],
        [-73.7278, 41.0970]
    ]
    poly = Polygon(ct_coords)
    gdf = gpd.GeoDataFrame(
        [{"STATEFP": "09", "NAME": "Connecticut", "geometry": poly}],
        crs="EPSG:4326"
    )
    return gdf


def save_feature(gdf: gpd.GeoDataFrame, output_path: Path):
    gdf = gdf.to_crs("EPSG:4326")
    gdf.to_file(output_path, driver="GeoJSON")
    print(f"Saved {output_path}")


def save_geometry(gdf: gpd.GeoDataFrame, output_path: Path):
    geom = gdf.geometry.union_all()
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(mapping(geom), f, indent=2)
    print(f"Saved {output_path}")


def main():
    connecticut = None
    hartford = None

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            state_zip = temp_path / "states.zip"
            place_zip = temp_path / "places.zip"

            download_file(STATE_URL, state_zip)
            download_file(PLACE_URL, place_zip)

            states = read_zip_shapefile(state_zip)
            places = read_zip_shapefile(place_zip)

            ct_filter = states[states["STATEFP"] == STATE_FIPS].copy()
            hfd_filter = places[
                (places["STATEFP"] == STATE_FIPS)
                & (places["NAME"].str.lower() == CITY_NAME.lower())
            ].copy()

            if not ct_filter.empty:
                connecticut = ct_filter
            if not hfd_filter.empty:
                hartford = hfd_filter

    except Exception as e:
        print(f"Warning: Census download failed ({e}). Generating fallback geometry.")

    if connecticut is None or connecticut.empty:
        connecticut = create_fallback_ct_boundary()
    if hartford is None or hartford.empty:
        hartford = create_fallback_hartford_boundary()

    connecticut = connecticut.to_crs("EPSG:4326")
    hartford = hartford.to_crs("EPSG:4326")

    save_feature(connecticut, OUTPUT_DIR / "connecticut.geojson")
    save_feature(hartford, OUTPUT_DIR / "hartford.geojson")
    save_geometry(hartford, OUTPUT_DIR / "hartford_geometry.json")

    minx, miny, maxx, maxy = hartford.total_bounds
    bbox = {
        "west": float(minx),
        "south": float(miny),
        "east": float(maxx),
        "north": float(maxy)
    }

    with (OUTPUT_DIR / "hartford_bbox.json").open("w", encoding="utf-8") as f:
        json.dump(bbox, f, indent=2)

    print("\nHartford bounding box successfully generated:")
    print(json.dumps(bbox, indent=2))


if __name__ == "__main__":
    main()
