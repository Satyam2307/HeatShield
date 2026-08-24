"""
Buffer creation for bus-stop analysis.

All meter-based operations use a projected CRS (Connecticut State Plane).
Results are converted back to EPSG:4326 for output.
"""

from __future__ import annotations

from shapely.geometry import Point
from shapely.ops import transform
import pyproj

from app.config import settings


def create_buffer_wgs84(
    lon: float,
    lat: float,
    radius_meters: int | None = None,
) -> dict:
    """
    Create a circular buffer around a point in WGS84 coordinates.

    Projects to Connecticut State Plane for accurate meter-based buffer,
    then reprojects back to WGS84.

    Args:
        lon: Longitude (WGS84).
        lat: Latitude (WGS84).
        radius_meters: Buffer radius. Defaults to config.

    Returns:
        GeoJSON-compatible polygon dict.
    """
    if radius_meters is None:
        radius_meters = settings.buffer.default_meters

    # Clamp to allowed range
    radius_meters = max(
        settings.buffer.min_meters,
        min(settings.buffer.max_meters, radius_meters),
    )

    # The projected CRS is CT State Plane in feet; convert meters to feet
    # EPSG:2234 is NAD83 / Connecticut (ftUS)
    # 1 meter = 3.28084 US survey feet
    radius_ft = radius_meters * 3.28084

    # Create transformers
    wgs84 = pyproj.CRS("EPSG:4326")
    projected = pyproj.CRS(settings.hartford_projected_crs)

    project_fwd = pyproj.Transformer.from_crs(wgs84, projected, always_xy=True).transform
    project_inv = pyproj.Transformer.from_crs(projected, wgs84, always_xy=True).transform

    # Project point, buffer, reproject
    point_proj = transform(project_fwd, Point(lon, lat))
    buffer_proj = point_proj.buffer(radius_ft)
    buffer_wgs84 = transform(project_inv, buffer_proj)

    # Convert to GeoJSON-like dict
    coords = list(buffer_wgs84.exterior.coords)
    return {
        "type": "Polygon",
        "coordinates": [[[round(x, 6), round(y, 6)] for x, y in coords]],
    }


def get_buffer_polygon(lon: float, lat: float, radius_meters: int = 100):
    """
    Return a Shapely Polygon buffer in WGS84.

    This is for spatial join operations where we need a Shapely object.
    """
    radius_ft = radius_meters * 3.28084
    wgs84 = pyproj.CRS("EPSG:4326")
    projected = pyproj.CRS(settings.hartford_projected_crs)

    project_fwd = pyproj.Transformer.from_crs(wgs84, projected, always_xy=True).transform
    project_inv = pyproj.Transformer.from_crs(projected, wgs84, always_xy=True).transform

    point_proj = transform(project_fwd, Point(lon, lat))
    buffer_proj = point_proj.buffer(radius_ft)
    return transform(project_inv, buffer_proj)
