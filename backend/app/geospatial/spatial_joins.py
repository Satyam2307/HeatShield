"""
Spatial join operations.

Joins bus stops to Census tracts (point-in-polygon) and
heat grid cells to stop buffers (intersection).
"""

from __future__ import annotations

from app.geospatial.boundary import point_in_hartford


def filter_stops_to_boundary(
    stops_geojson: dict,
    boundary_polygon: list[list[float]] | None = None,
) -> dict:
    """
    Filter bus stops to only those within the Hartford boundary.

    Args:
        stops_geojson: GeoJSON FeatureCollection of bus stops.
        boundary_polygon: Hartford boundary coordinates.

    Returns:
        Filtered GeoJSON FeatureCollection.
    """
    filtered = []
    for feature in stops_geojson.get("features", []):
        coords = feature["geometry"]["coordinates"]
        lon, lat = coords[0], coords[1]
        if point_in_hartford(lon, lat, boundary_polygon):
            filtered.append(feature)

    return {
        "type": "FeatureCollection",
        "features": filtered,
    }


def assign_stop_to_tract(
    stop_lon: float,
    stop_lat: float,
    tracts_geojson: dict,
) -> str | None:
    """
    Assign a bus stop to its containing Census tract (point-in-polygon).

    Returns the tract GEOID, or None if the stop doesn't fall in any tract.
    """
    for feature in tracts_geojson.get("features", []):
        polygon = feature["geometry"]["coordinates"][0]
        if _point_in_polygon(stop_lon, stop_lat, polygon):
            return feature["properties"]["GEOID"]
    return None


def _point_in_polygon(lon: float, lat: float, polygon: list[list[float]]) -> bool:
    """Ray-casting point-in-polygon test."""
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
