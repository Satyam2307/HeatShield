"""
Transit data adapter.

Loads bus-stop data from GTFS or GeoJSON sources.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.config import FIXTURES_DIR
from app.geospatial.boundary import get_hartford_polygon
from app.geospatial.spatial_joins import filter_stops_to_boundary


class TransitAdapter:
    """Adapter for loading and filtering transit stop data."""

    def load_stops(self, source_path: str | Path | None = None) -> dict:
        """
        Load bus stops from file.

        Args:
            source_path: Path to GeoJSON file. Defaults to fixture data.

        Returns:
            GeoJSON FeatureCollection of bus stops within Hartford.
        """
        if source_path is None:
            source_path = FIXTURES_DIR / "hartford_bus_stops.geojson"

        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"Bus stop data not found at {path}")

        with open(path) as f:
            stops = json.load(f)

        # Filter to Hartford boundary
        polygon = get_hartford_polygon()
        filtered = filter_stops_to_boundary(stops, polygon)

        return filtered

    def get_stop_count(self, stops: dict | None = None) -> int:
        """Return number of stops."""
        if stops is None:
            stops = self.load_stops()
        return len(stops.get("features", []))


transit_adapter = TransitAdapter()
