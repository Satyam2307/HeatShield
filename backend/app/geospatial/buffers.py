"""
Buffer creation for bus-stop analysis.

All meter-based operations use a projected CRS (Connecticut State Plane).
Results are converted back to EPSG:4326 for output.
"""

from __future__ import annotations

import math

try:
    from shapely.geometry import Point
    from shapely.ops import transform
    import pyproj
    HAS_PYPROJ = True
except Exception:
    HAS_PYPROJ = False

from app.config import settings


def _pure_python_buffer(lon: float, lat: float, radius_meters: float) -> dict:
    """Pure Python geodesic circular buffer fallback without external C dependencies."""
    num_points = 32
    coords = []
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    d = radius_meters / 6371000.0  # Earth radius in meters

    for i in range(num_points + 1):
        bearing = 2 * math.pi * i / num_points
        lat_out = math.asin(
            math.sin(lat_rad) * math.cos(d)
            + math.cos(lat_rad) * math.sin(d) * math.cos(bearing)
        )
        lon_out = lon_rad + math.atan2(
            math.sin(bearing) * math.sin(d) * math.cos(lat_rad),
            math.cos(d) - math.sin(lat_rad) * math.sin(lat_out),
        )
        coords.append([round(math.degrees(lon_out), 6), round(math.degrees(lat_out), 6)])

    return {
        "type": "Polygon",
        "coordinates": [coords],
    }


def create_buffer_wgs84(
    lon: float,
    lat: float,
    radius_meters: int | None = None,
) -> dict:
    """
    Create a circular buffer around a point in WGS84 coordinates.
    """
    if radius_meters is None:
        radius_meters = settings.buffer.default_meters

    radius_meters = max(
        settings.buffer.min_meters,
        min(settings.buffer.max_meters, radius_meters),
    )

    if not HAS_PYPROJ:
        return _pure_python_buffer(lon, lat, radius_meters)

    try:
        radius_ft = radius_meters * 3.28084
        wgs84 = pyproj.CRS("EPSG:4326")
        projected = pyproj.CRS(settings.hartford_projected_crs)

        project_fwd = pyproj.Transformer.from_crs(wgs84, projected, always_xy=True).transform
        project_inv = pyproj.Transformer.from_crs(projected, wgs84, always_xy=True).transform

        point_proj = transform(project_fwd, Point(lon, lat))
        buffer_proj = point_proj.buffer(radius_ft)
        buffer_wgs84 = transform(project_inv, buffer_proj)

        coords = list(buffer_wgs84.exterior.coords)
        return {
            "type": "Polygon",
            "coordinates": [[[round(x, 6), round(y, 6)] for x, y in coords]],
        }
    except Exception:
        return _pure_python_buffer(lon, lat, radius_meters)


def get_buffer_polygon(lon: float, lat: float, radius_meters: int = 100):
    """Return buffer polygon object or coordinates."""
    if HAS_PYPROJ:
        try:
            radius_ft = radius_meters * 3.28084
            wgs84 = pyproj.CRS("EPSG:4326")
            projected = pyproj.CRS(settings.hartford_projected_crs)

            project_fwd = pyproj.Transformer.from_crs(wgs84, projected, always_xy=True).transform
            project_inv = pyproj.Transformer.from_crs(projected, wgs84, always_xy=True).transform

            point_proj = transform(project_fwd, Point(lon, lat))
            buffer_proj = point_proj.buffer(radius_ft)
            return transform(project_inv, buffer_proj)
        except Exception:
            pass
    return _pure_python_buffer(lon, lat, radius_meters)
