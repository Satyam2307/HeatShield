"""
HeatShield: ShadeStop — Application Configuration

Loads settings from environment variables with sensible defaults.
Supports fixture mode for hackathon demos without external dependencies.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Resolve project root (two levels up from this file: backend/app/config.py)
# ---------------------------------------------------------------------------
_THIS_DIR = Path(__file__).resolve().parent
BACKEND_DIR = _THIS_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

# ---------------------------------------------------------------------------
# Path helpers — support both local monorepo and Vercel backend bundle
# ---------------------------------------------------------------------------
if (PROJECT_ROOT / "data" / "fixtures").exists():
    DATA_DIR = PROJECT_ROOT / "data"
elif (BACKEND_DIR / "data" / "fixtures").exists():
    DATA_DIR = BACKEND_DIR / "data"
else:
    DATA_DIR = Path.cwd() / "data"

BOUNDARIES_DIR = DATA_DIR / "boundaries"
FIXTURES_DIR = DATA_DIR / "fixtures"
PROCESSED_DIR = DATA_DIR / "processed"
CACHE_DIR = Path("/tmp/cache") if os.getenv("VERCEL") else Path(os.getenv("CACHE_DIR", str(DATA_DIR / "cache")))


# ---------------------------------------------------------------------------
# Scoring weight defaults
# ---------------------------------------------------------------------------
class ScoringWeightsConfig(BaseModel):
    """Default weights for the priority score formula."""

    heat: float = 0.40
    shade: float = 0.25
    vulnerability: float = 0.20
    transit: float = 0.15

    # Heat sub-component weights
    heat_cumulative_exceedance: float = 0.50
    heat_dangerous_minutes: float = 0.30
    heat_persistence: float = 0.20


class InterventionScenarioConfig(BaseModel):
    """Configuration for a single intervention planning scenario."""

    effectiveness_factor: float
    coverage_factor: float


class InterventionConfig(BaseModel):
    """All intervention scenario presets."""

    conservative: InterventionScenarioConfig = InterventionScenarioConfig(
        effectiveness_factor=0.20, coverage_factor=0.70
    )
    moderate: InterventionScenarioConfig = InterventionScenarioConfig(
        effectiveness_factor=0.35, coverage_factor=0.80
    )
    high: InterventionScenarioConfig = InterventionScenarioConfig(
        effectiveness_factor=0.50, coverage_factor=0.90
    )


class BufferConfig(BaseModel):
    """Bus-stop analysis buffer configuration (metres)."""

    default_meters: int = 100
    min_meters: int = 25
    max_meters: int = 500


# ---------------------------------------------------------------------------
# Main settings
# ---------------------------------------------------------------------------
class Settings(BaseModel):
    """Application-wide settings populated from environment variables."""

    # General
    environment: Literal["development", "staging", "production"] = "development"
    data_mode: Literal["fixture", "live"] = "fixture"
    app_version: str = "0.1.0"
    scoring_version: str = "v1.0"

    # Database (optional — unused in fixture mode)
    database_url: str = ""

    # Cache
    redis_url: str = ""
    cache_dir: str = str(CACHE_DIR)

    # FortyGuard
    fortyguard_base_url: str = ""
    fortyguard_api_key: str = ""
    fortyguard_timeout_seconds: int = 30
    fortyguard_max_retries: int = 2

    # Census / ACS
    census_api_key: str = ""

    # LLM (optional — for AI explanations)
    llm_api_key: str = ""

    # Geospatial
    buffer: BufferConfig = BufferConfig()
    hartford_projected_crs: str = "EPSG:2234"  # Connecticut State Plane (ft)
    default_crs: str = "EPSG:4326"

    # Scoring
    scoring_weights: ScoringWeightsConfig = ScoringWeightsConfig()

    # Intervention
    intervention: InterventionConfig = InterventionConfig()

    # Analysis defaults
    default_heat_metric: str = "heat_index"
    default_heat_unit: str = "F"
    default_danger_threshold: float = 95.0
    default_interval_minutes: int = 60

    # Hartford fixture defaults
    default_analysis_date: str = "2023-07-27"  # Hartford heatwave
    default_start_hour: int = 10
    default_end_hour: int = 18

    class Config:
        extra = "ignore"


def load_settings() -> Settings:
    """Load settings from environment variables."""
    env_vars = {
        "environment": os.getenv("ENVIRONMENT", "development"),
        "data_mode": os.getenv("DATA_MODE", "fixture"),
        "database_url": os.getenv("DATABASE_URL", ""),
        "redis_url": os.getenv("REDIS_URL", ""),
        "cache_dir": os.getenv("CACHE_DIR", str(CACHE_DIR)),
        "fortyguard_base_url": os.getenv("FORTYGUARD_BASE_URL", ""),
        "fortyguard_api_key": os.getenv("FORTYGUARD_API_KEY", ""),
        "census_api_key": os.getenv("CENSUS_API_KEY", ""),
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
    }
    return Settings(**env_vars)


# Singleton — import `settings` elsewhere
settings = load_settings()
