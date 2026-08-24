"""
Fixture service — loads and serves precomputed Hartford data.

When DATA_MODE=fixture, the entire backend runs from these files
with no external API calls.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from app.config import FIXTURES_DIR, BOUNDARIES_DIR


@lru_cache(maxsize=1)
def load_boundary() -> dict:
    """Load Hartford city boundary GeoJSON."""
    path = BOUNDARIES_DIR / "hartford_geometry.geojson"
    with open(path) as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_bus_stops() -> dict:
    """Load Hartford bus stops GeoJSON."""
    path = FIXTURES_DIR / "hartford_bus_stops.geojson"
    with open(path) as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_heat_observations() -> dict:
    """Load heat observations keyed by stop_id."""
    path = FIXTURES_DIR / "hartford_heat_observations.json"
    with open(path) as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_shade_metrics() -> dict:
    """Load shade metrics keyed by stop_id."""
    path = FIXTURES_DIR / "hartford_shade_metrics.json"
    with open(path) as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_vulnerability() -> dict:
    """Load vulnerability data keyed by stop_id."""
    path = FIXTURES_DIR / "hartford_vulnerability.json"
    with open(path) as f:
        return json.load(f)


@lru_cache(maxsize=1)
def load_census_tracts() -> dict:
    """Load Census tracts GeoJSON."""
    path = FIXTURES_DIR / "hartford_census_tracts.geojson"
    with open(path) as f:
        return json.load(f)


def get_stop_ids() -> list[str]:
    """Return list of all stop IDs."""
    stops = load_bus_stops()
    return [f["properties"]["id"] for f in stops["features"]]


def get_stop_by_id(stop_id: str) -> dict | None:
    """Return a single stop feature by ID."""
    stops = load_bus_stops()
    for feature in stops["features"]:
        if feature["properties"]["id"] == stop_id:
            return feature
    return None


def get_heat_timeseries(stop_id: str) -> list[dict] | None:
    """Return heat observations for a specific stop."""
    heat = load_heat_observations()
    return heat.get(stop_id)


def get_shade_for_stop(stop_id: str) -> dict | None:
    """Return shade metrics for a specific stop."""
    shade = load_shade_metrics()
    return shade.get(stop_id)


def get_vulnerability_for_stop(stop_id: str) -> dict | None:
    """Return vulnerability indicators for a specific stop."""
    vuln = load_vulnerability()
    return vuln.get(stop_id)
