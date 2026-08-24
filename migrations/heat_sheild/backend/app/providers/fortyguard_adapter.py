"""
FortyGuard Adapter for live requests and offline fixture data management.
"""

from pathlib import Path
import json
from typing import Dict, Any, Optional
from ..config import settings

FIXTURE_PATH = Path("data/fixtures/hartford_demo.json")
GEOJSON_PATH = Path("data/processed/hartford_priority_scores.geojson")

class FortyGuardAdapterService:
    def __init__(self):
        self.mode = settings.DATA_MODE
        self.base_url = settings.FORTYGUARD_BASE_URL
        self.api_key = settings.FORTYGUARD_API_KEY

    def load_demo_fixture(self) -> Dict[str, Any]:
        if not FIXTURE_PATH.exists():
            raise FileNotFoundError(f"Fixture file not found at {FIXTURE_PATH}")
        with FIXTURE_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)

    def load_map_geojson(self) -> Dict[str, Any]:
        if not GEOJSON_PATH.exists():
            raise FileNotFoundError(f"GeoJSON file not found at {GEOJSON_PATH}")
        with GEOJSON_PATH.open("r", encoding="utf-8") as f:
            return json.load(f)

fortyguard_service = FortyGuardAdapterService()
