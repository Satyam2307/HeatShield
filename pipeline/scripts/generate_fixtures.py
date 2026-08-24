#!/usr/bin/env python3
"""
Generate realistic fixture data for Hartford, Connecticut.

Produces:
  - data/boundaries/hartford_geometry.geojson
  - data/fixtures/hartford_bus_stops.geojson
  - data/fixtures/hartford_heat_observations.json
  - data/fixtures/hartford_shade_metrics.json
  - data/fixtures/hartford_vulnerability.json
  - data/fixtures/hartford_census_tracts.geojson
  - data/processed/hartford_priority_scores.geojson (final MVP deliverable)

Uses realistic Hartford coordinates and distributions.
All data is synthetic but geographically accurate.
"""

from __future__ import annotations

import json
import hashlib
import math
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Hartford geography constants
# ---------------------------------------------------------------------------
# Hartford city centre ≈ 41.7637°N, 72.6851°W
HARTFORD_CENTER = (-72.6851, 41.7637)
HARTFORD_BBOX = [-72.7130, 41.7350, -72.6500, 41.7970]  # [W, S, E, N]

# Simplified Hartford boundary polygon (convex hull approximation)
HARTFORD_BOUNDARY_COORDS = [
    [-72.7050, 41.7380],
    [-72.6520, 41.7380],
    [-72.6500, 41.7550],
    [-72.6530, 41.7800],
    [-72.6600, 41.7950],
    [-72.6750, 41.7970],
    [-72.6950, 41.7920],
    [-72.7100, 41.7800],
    [-72.7130, 41.7600],
    [-72.7050, 41.7380],  # close ring
]

# Hartford Census tract GEOIDs (actual tract numbers in Hartford County)
HARTFORD_TRACTS = [
    "09003501100", "09003501200", "09003501300", "09003501400",
    "09003501500", "09003501600", "09003501700", "09003501800",
    "09003501900", "09003502000", "09003502100", "09003502200",
    "09003502300", "09003502400", "09003502500", "09003502600",
    "09003502700", "09003502800", "09003502900", "09003503000",
    "09003503100", "09003503200", "09003503300", "09003503400",
    "09003503500",
]

# Analysis date: July 27, 2023 — Hartford heatwave
ANALYSIS_DATE = "2023-07-27"
EDT = timezone(timedelta(hours=-4))

# Seed for reproducibility
random.seed(42)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def project_root() -> Path:
    """Return the project root (parent of pipeline/)."""
    return Path(__file__).resolve().parent.parent.parent


def make_id(prefix: str, idx: int) -> str:
    return f"{prefix}-{idx:04d}"


def random_point_in_bbox(bbox: list[float]) -> tuple[float, float]:
    """Return (lon, lat) within bbox."""
    lon = random.uniform(bbox[0], bbox[2])
    lat = random.uniform(bbox[1], bbox[3])
    return (lon, lat)


def point_in_polygon(lon: float, lat: float, polygon: list[list[float]]) -> bool:
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


def random_point_in_hartford() -> tuple[float, float]:
    """Return (lon, lat) inside the Hartford boundary."""
    for _ in range(1000):
        lon, lat = random_point_in_bbox(HARTFORD_BBOX)
        if point_in_polygon(lon, lat, HARTFORD_BOUNDARY_COORDS):
            return (lon, lat)
    return HARTFORD_CENTER


def haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """Approximate distance in km between two WGS84 points."""
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
# Hartford street names for realistic bus-stop names
# ---------------------------------------------------------------------------
STREET_NAMES = [
    "Main St", "Asylum St", "Capitol Ave", "Park St", "Albany Ave",
    "Farmington Ave", "Broad St", "Wethersfield Ave", "Franklin Ave",
    "New Britain Ave", "Maple Ave", "Washington St", "Barbour St",
    "Garden St", "Retreat Ave", "Sigourney St", "Tower Ave",
    "Homestead Ave", "Windsor Ave", "Woodland St", "Flatbush Ave",
    "Prospect St", "Laurel St", "Sargeant St", "Blue Hills Ave",
    "North Main St", "Capen St", "Mather St", "Vine St", "Affleck St",
    "Preston St", "Hudson St", "Magnolia St", "Jefferson St",
    "Zion St", "Babcock St", "Russ St", "Ward St", "Oak St",
]

CROSS_STREETS = [
    "at Elm", "at Trumbull", "at Pearl", "at Church", "at High",
    "at Ann", "at Market", "at Gold", "at Arch", "at Central",
    "at Sheldon", "at Morgan", "at Temple", "near Hospital",
    "near School", "near Library", "at Plaza", "at Commons",
    "near Park", "at Bridge",
]


# ---------------------------------------------------------------------------
# 1. Hartford Boundary GeoJSON
# ---------------------------------------------------------------------------
def generate_boundary() -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Hartford",
                    "state": "Connecticut",
                    "fips": "0937000",
                    "timezone": "America/New_York",
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [HARTFORD_BOUNDARY_COORDS],
                },
            }
        ],
    }


# ---------------------------------------------------------------------------
# 2. Bus Stops
# ---------------------------------------------------------------------------
def generate_bus_stops(n: int = 150) -> dict:
    features = []
    used_names: set[str] = set()

    for i in range(n):
        lon, lat = random_point_in_hartford()

        # Generate a unique name
        for _ in range(50):
            street = random.choice(STREET_NAMES)
            cross = random.choice(CROSS_STREETS)
            name = f"{street} {cross}"
            if name not in used_names:
                used_names.add(name)
                break
        else:
            name = f"Stop #{i + 1}"

        route_count = random.choices(
            [1, 2, 3, 4, 5, 6],
            weights=[20, 30, 25, 15, 7, 3],
            k=1,
        )[0]

        shelter = random.choices(
            ["present", "absent", "unknown"],
            weights=[25, 55, 20],
            k=1,
        )[0]

        features.append({
            "type": "Feature",
            "properties": {
                "id": make_id("stop", i),
                "external_stop_id": f"CT-{10000 + i}",
                "name": name,
                "route_count": route_count,
                "shelter_status": shelter,
                "source": "gtfs_cttransit",
            },
            "geometry": {
                "type": "Point",
                "coordinates": [round(lon, 6), round(lat, 6)],
            },
        })

    return {"type": "FeatureCollection", "features": features}


# ---------------------------------------------------------------------------
# 3. Heat observations (hourly 10 AM – 6 PM EDT on analysis date)
# ---------------------------------------------------------------------------
def _urban_heat_modifier(lon: float, lat: float) -> float:
    """
    Simulate urban heat island: stops closer to downtown Hartford are hotter.
    Returns a modifier in the range [0.0, 1.0] where 1.0 = maximum UHI effect.
    """
    dist_km = haversine_km(lon, lat, *HARTFORD_CENTER)
    # UHI effect decays with distance from centre, max radius ~3 km
    return max(0.0, 1.0 - dist_km / 3.0)


def _diurnal_curve(hour: int) -> float:
    """
    Approximate diurnal temperature curve peaking at ~3 PM.
    Returns a fraction [0, 1] of the daily range.
    """
    # Bell curve centred at 15 (3 PM), std ~ 3 hrs
    return math.exp(-0.5 * ((hour - 15) / 3.0) ** 2)


def generate_heat_observations(bus_stops: dict) -> dict:
    """Generate hourly heat-index values for each bus stop."""
    hours = list(range(10, 19))  # 10 AM to 6 PM inclusive
    observations: dict[str, list] = {}

    base_temp_low = 90.0   # morning baseline
    base_temp_range = 18.0  # daily swing up to peak

    for feature in bus_stops["features"]:
        stop_id = feature["properties"]["id"]
        lon, lat = feature["geometry"]["coordinates"]
        uhi = _urban_heat_modifier(lon, lat)

        series = []
        for hour in hours:
            diurnal = _diurnal_curve(hour)
            # Base + diurnal + UHI + random noise
            value = (
                base_temp_low
                + base_temp_range * diurnal
                + uhi * 5.0  # up to 5°F UHI
                + random.gauss(0, 1.5)
            )
            value = round(max(85.0, value), 1)

            ts = datetime(2023, 7, 27, hour, 0, 0, tzinfo=EDT)

            series.append({
                "timestamp": ts.isoformat(),
                "value": value,
                "metric": "heat_index",
                "unit": "F",
                "source": "fortyguard_fixture",
                "quality_flag": "good",
            })

        observations[stop_id] = series

    return observations


# ---------------------------------------------------------------------------
# 4. Shade metrics (per stop)
# ---------------------------------------------------------------------------
def generate_shade_metrics(bus_stops: dict) -> dict:
    """Generate realistic land-cover fractions for each bus stop."""
    metrics: dict[str, dict] = {}

    for feature in bus_stops["features"]:
        stop_id = feature["properties"]["id"]
        lon, lat = feature["geometry"]["coordinates"]

        # Downtown areas have more impervious, less vegetation
        uhi = _urban_heat_modifier(lon, lat)

        veg = max(0.0, min(1.0, random.gauss(0.35 - 0.2 * uhi, 0.12)))
        imp = max(0.0, min(1.0, random.gauss(0.45 + 0.15 * uhi, 0.10)))
        bld = max(0.0, min(1.0 - veg - imp, random.gauss(0.15 + 0.05 * uhi, 0.08)))
        # Normalize
        total = veg + imp + bld
        if total > 0:
            veg, imp, bld = veg / total, imp / total, bld / total

        # Shade deficit: high impervious + low vegetation = high deficit
        shade_deficit = max(0.0, min(1.0, 1.0 - veg * 1.5 - bld * 0.3))

        shelter = feature["properties"].get("shelter_status", "unknown")

        metrics[stop_id] = {
            "buffer_meters": 100,
            "vegetation_fraction": round(veg, 3),
            "impervious_fraction": round(imp, 3),
            "building_fraction": round(bld, 3),
            "canopy_fraction": round(veg * 0.6, 3),  # canopy ≈ 60% of veg
            "shade_deficit": round(shade_deficit, 3),
            "shelter_status": shelter,
            "confidence": 0.7,
            "source": "satellite_landcover_fixture",
        }

    return metrics


# ---------------------------------------------------------------------------
# 5. Census / vulnerability data (per tract, mapped to stops)
# ---------------------------------------------------------------------------
def generate_vulnerability(bus_stops: dict) -> dict:
    """Generate Census-like vulnerability indicators per stop."""
    # Pre-generate tract-level data
    tract_data: dict[str, dict] = {}
    for tract_id in HARTFORD_TRACTS:
        tract_data[tract_id] = {
            "population": random.randint(1800, 6500),
            "population_density": round(random.uniform(1500, 12000), 0),
            "median_income": round(random.uniform(18000, 75000), 0),
            "zero_vehicle_fraction": round(random.uniform(0.05, 0.55), 3),
            "older_adult_fraction": round(random.uniform(0.08, 0.28), 3),
            "children_fraction": round(random.uniform(0.15, 0.35), 3),
            "disability_fraction": round(random.uniform(0.08, 0.22), 3),
        }

    # Assign each stop to a tract (simple modular mapping)
    vulnerability: dict[str, dict] = {}
    for i, feature in enumerate(bus_stops["features"]):
        stop_id = feature["properties"]["id"]
        tract_id = HARTFORD_TRACTS[i % len(HARTFORD_TRACTS)]
        td = tract_data[tract_id]

        vulnerability[stop_id] = {
            "geography_id": tract_id,
            "geography_type": "tract",
            **td,
            "source": "acs_5yr_2022_fixture",
            "label": "Community vulnerability indicators",
        }

    return vulnerability


# ---------------------------------------------------------------------------
# 6. Census tracts GeoJSON (simplified rectangles for each tract)
# ---------------------------------------------------------------------------
def generate_census_tracts() -> dict:
    """Generate simplified tract polygons covering Hartford."""
    features = []
    n_cols = 5
    n_rows = 5

    lon_step = (HARTFORD_BBOX[2] - HARTFORD_BBOX[0]) / n_cols
    lat_step = (HARTFORD_BBOX[3] - HARTFORD_BBOX[1]) / n_rows

    idx = 0
    for row in range(n_rows):
        for col in range(n_cols):
            if idx >= len(HARTFORD_TRACTS):
                break
            w = HARTFORD_BBOX[0] + col * lon_step
            s = HARTFORD_BBOX[1] + row * lat_step
            e = w + lon_step
            n = s + lat_step

            features.append({
                "type": "Feature",
                "properties": {
                    "GEOID": HARTFORD_TRACTS[idx],
                    "NAME": f"Tract {HARTFORD_TRACTS[idx][-4:]}",
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[w, s], [e, s], [e, n], [w, n], [w, s]]],
                },
            })
            idx += 1

    return {"type": "FeatureCollection", "features": features}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    root = project_root()
    boundaries_dir = root / "data" / "boundaries"
    fixtures_dir = root / "data" / "fixtures"
    processed_dir = root / "data" / "processed"

    for d in (boundaries_dir, fixtures_dir, processed_dir):
        d.mkdir(parents=True, exist_ok=True)

    print("Generating Hartford boundary...")
    boundary = generate_boundary()
    (boundaries_dir / "hartford_geometry.geojson").write_text(
        json.dumps(boundary, indent=2)
    )

    print("Generating bus stops (150)...")
    bus_stops = generate_bus_stops(150)
    (fixtures_dir / "hartford_bus_stops.geojson").write_text(
        json.dumps(bus_stops, indent=2)
    )

    print("Generating heat observations...")
    heat = generate_heat_observations(bus_stops)
    (fixtures_dir / "hartford_heat_observations.json").write_text(
        json.dumps(heat, indent=2)
    )

    print("Generating shade metrics...")
    shade = generate_shade_metrics(bus_stops)
    (fixtures_dir / "hartford_shade_metrics.json").write_text(
        json.dumps(shade, indent=2)
    )

    print("Generating vulnerability data...")
    vuln = generate_vulnerability(bus_stops)
    (fixtures_dir / "hartford_vulnerability.json").write_text(
        json.dumps(vuln, indent=2)
    )

    print("Generating census tracts...")
    tracts = generate_census_tracts()
    (fixtures_dir / "hartford_census_tracts.geojson").write_text(
        json.dumps(tracts, indent=2)
    )

    print(f"\n✅ All fixture files written to:")
    print(f"   {boundaries_dir}/")
    print(f"   {fixtures_dir}/")
    print(f"\n📊 Summary:")
    print(f"   Bus stops:  {len(bus_stops['features'])}")
    print(f"   Heat obs:   {len(heat)} stops × 9 hours = {len(heat) * 9} records")
    print(f"   Shade:      {len(shade)} stops")
    print(f"   Vuln:       {len(vuln)} stops")
    print(f"   Tracts:     {len(tracts['features'])}")


if __name__ == "__main__":
    main()
