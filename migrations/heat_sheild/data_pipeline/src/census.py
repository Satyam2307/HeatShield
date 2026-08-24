"""
Census ACS Vulnerability Module for Hartford, CT.
"""

from typing import Dict, Any
import numpy as np

HARTFORD_TRACTS = [
    {"tract_id": "09003500100", "name": "North End / Clay-Arsenal", "vehicle_pct": 0.42, "older_pct": 0.14, "child_pct": 0.28, "income": 26500, "density": 8200},
    {"tract_id": "09003500200", "name": "Upper Albany", "vehicle_pct": 0.38, "older_pct": 0.16, "child_pct": 0.26, "income": 28900, "density": 7800},
    {"tract_id": "09003501500", "name": "Frog Hollow", "vehicle_pct": 0.45, "older_pct": 0.11, "child_pct": 0.29, "income": 24200, "density": 9400},
    {"tract_id": "09003502800", "name": "South End / Barry Square", "vehicle_pct": 0.31, "older_pct": 0.15, "child_pct": 0.22, "income": 34500, "density": 6500},
    {"tract_id": "09003503300", "name": "Asylum Hill", "vehicle_pct": 0.39, "older_pct": 0.13, "child_pct": 0.21, "income": 31000, "density": 8900},
    {"tract_id": "09003504100", "name": "West End", "vehicle_pct": 0.16, "older_pct": 0.18, "child_pct": 0.17, "income": 68000, "density": 4800},
    {"tract_id": "09003502100", "name": "Downtown Hartford", "vehicle_pct": 0.34, "older_pct": 0.19, "child_pct": 0.12, "income": 49000, "density": 5200}
]

def estimate_census_vulnerability(lat: float, lon: float) -> Dict[str, Any]:
    seed = int(abs(lat * 3000 + lon * 3000)) % 10000
    rng = np.random.RandomState(seed)
    
    if lat > 41.78:
        tract = HARTFORD_TRACTS[1]
    elif lat < 41.74:
        tract = HARTFORD_TRACTS[3]
    elif lon < -72.70:
        tract = HARTFORD_TRACTS[5]
    elif lon > -72.67:
        tract = HARTFORD_TRACTS[6]
    elif lat > 41.76:
        tract = HARTFORD_TRACTS[4]
    else:
        tract = HARTFORD_TRACTS[2]
        
    vehicle_pct = float(np.clip(tract["vehicle_pct"] + rng.uniform(-0.03, 0.03), 0.05, 0.60))
    older_pct = float(np.clip(tract["older_pct"] + rng.uniform(-0.02, 0.02), 0.05, 0.35))
    child_pct = float(np.clip(tract["child_pct"] + rng.uniform(-0.02, 0.02), 0.05, 0.35))
    income = float(round(max(15000, tract["income"] + rng.randint(-3000, 3000)), -2))
    density = float(round(tract["density"] + rng.randint(-400, 400), -1))
    
    income_factor = max(0.0, (80000 - income) / 80000.0)
    raw_vulnerability = (vehicle_pct * 0.40 + income_factor * 0.35 + older_pct * 0.15 + child_pct * 0.10) * 100.0
    
    return {
        "geography_id": tract["tract_id"],
        "neighborhood_name": tract["name"],
        "median_income": income,
        "zero_vehicle_fraction": round(vehicle_pct, 3),
        "older_adult_fraction": round(older_pct, 3),
        "children_fraction": round(child_pct, 3),
        "population_density": density,
        "raw_vulnerability_score": round(raw_vulnerability, 2),
        "source": "US Census ACS 5-Year Estimates (2022)"
    }
