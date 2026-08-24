"""
Geospatial boundary utilities.

Loads and validates the Hartford city boundary.
Handles CRS conversions.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.config import BOUNDARIES_DIR


def load_hartford_boundary() -> dict:
    """
    Load Hartford city boundary GeoJSON with fallback candidates.
    """
    candidates = [
        BOUNDARIES_DIR / "hartford_geometry.geojson",
        BOUNDARIES_DIR / "hartford_geometry.json",
        BOUNDARIES_DIR / "hartford.geojson",
    ]
    path = None
    for cand in candidates:
        if cand.exists():
            path = cand
            break

    if not path:
        raise FileNotFoundError(f"Hartford boundary file not found in {BOUNDARIES_DIR}")

    with open(path) as f:
        geojson = json.load(f)

    _validate_geojson(geojson)
    return geojson


def get_hartford_polygon(boundary: dict | None = None) -> list[list[float]]:
    """Extract the polygon coordinates from Hartford boundary GeoJSON."""
    if boundary is None:
        boundary = load_hartford_boundary()

    feature = boundary["features"][0]
    return feature["geometry"]["coordinates"][0]


def get_hartford_bbox(boundary: dict | None = None) -> list[float]:
    """Calculate bounding box [west, south, east, north] from boundary."""
    polygon = get_hartford_polygon(boundary)
    lons = [p[0] for p in polygon]
    lats = [p[1] for p in polygon]
    return [min(lons), min(lats), max(lons), max(lats)]


def point_in_hartford(
    lon: float,
    lat: float,
    polygon: list[list[float]] | None = None,
) -> bool:
    """Check if a point is inside the Hartford boundary using ray-casting."""
    if polygon is None:
        polygon = get_hartford_polygon()

    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def _validate_geojson(geojson: dict) -> None:
    """Basic validation of GeoJSON structure."""
    if geojson.get("type") != "FeatureCollection":
        raise ValueError("Expected GeoJSON FeatureCollection")
    if not geojson.get("features"):
        raise ValueError("Empty FeatureCollection")
    feature = geojson["features"][0]
    if feature.get("type") != "Feature":
        raise ValueError("Expected Feature")
    if "geometry" not in feature:
        raise ValueError("Feature missing geometry")
