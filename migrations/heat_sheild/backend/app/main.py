"""
Main FastAPI Application Entry Point for HeatShield: ShadeStop (Hartford, CT).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import router as api_router

app = FastAPI(
    title="HeatShield: ShadeStop API",
    description="Backend service for Hartford bus stop heat intervention prioritization platform.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "HeatShield: ShadeStop",
        "city": "Hartford, CT",
        "version": "1.0.0"
    }
