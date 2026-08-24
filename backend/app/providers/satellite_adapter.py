"""
Satellite/land-cover data adapter.

Loads shade and vegetation data from satellite sources or fixture files.
"""

from __future__ import annotations

import json
from pathlib import Path

from app.config import FIXTURES_DIR


class SatelliteAdapter:
    """Adapter for satellite land-cover / shade data."""

    def load_shade_metrics(self, source_path: str | Path | None = None) -> dict:
        """
        Load shade metrics keyed by stop_id.

        In fixture mode, loads from pre-computed JSON.
        In live mode, would process satellite imagery.
        """
        if source_path is None:
            source_path = FIXTURES_DIR / "hartford_shade_metrics.json"

        path = Path(source_path)
        if not path.exists():
            raise FileNotFoundError(f"Shade metrics not found at {path}")

        with open(path) as f:
            return json.load(f)


satellite_adapter = SatelliteAdapter()
