"""
HeatShield: ShadeStop — FastAPI Application

Hartford bus-stop heat intervention prioritization platform.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Add backend directory to sys.path for serverless execution on Vercel
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api import health, cities, analysis, assets, interventions, explanations, reports

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("heatshield")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="HeatShield: ShadeStop",
    description=(
        "Rank Hartford bus stops by heat-intervention priority and "
        "simulate the impact of adding shade structures."
    ),
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — allow frontend dev server
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(health.router)
app.include_router(cities.router)
app.include_router(analysis.router)
app.include_router(assets.router)
app.include_router(interventions.router)
app.include_router(explanations.router)
app.include_router(reports.router)

# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup():
    logger.info(
        "HeatShield starting — env=%s data_mode=%s version=%s",
        settings.environment,
        settings.data_mode,
        settings.app_version,
    )

    # Pre-warm fixture data if in fixture mode
    if settings.data_mode == "fixture":
        from app.services import analysis_service
        logger.info("Pre-warming fixture analysis...")
        analysis_service.run_analysis(analysis_id="fixture-001")
        # Save the MVP GeoJSON deliverable
        path = analysis_service.save_priority_geojson("fixture-001")
        logger.info("MVP GeoJSON saved to %s", path)


# ---------------------------------------------------------------------------
# Root redirect
# ---------------------------------------------------------------------------
@app.get("/", include_in_schema=False)
async def root():
    return {"message": "HeatShield: ShadeStop API", "docs": "/docs"}
