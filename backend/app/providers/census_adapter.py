"""
Census/ACS data adapter.

Loads community vulnerability indicator data from Census API or fixture files.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.config import FIXTURES_DIR


class CensusAdapter:
    """Adapter for Census/ACS community vulnerability data."""

    def load_vulnerability_data(self, source_path: str | Path | None = None) -> dict:
        """
        Load vulnerability indicators keyed by stop_id.

        In fixture mode, loads from pre-computed JSON.
        In live mode, would query the Census API.
        """
        if source_path is None:
            source_path = FIXTURES_DIR / "hartford_vulnerability.json"

        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"Vulnerability data not found at {path}")

        with open(path) as f:
            return json.load(f)

    def load_census_tracts(self, source_path: str | Path | None = None) -> dict:
        """Load Census tract boundaries GeoJSON."""
        if source_path is None:
            source_path = FIXTURES_DIR / "hartford_census_tracts.geojson"

        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"Census tracts not found at {path}")

        with open(path) as f:
            return json.load(f)


census_adapter = CensusAdapter()
