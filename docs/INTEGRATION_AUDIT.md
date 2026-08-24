# HeatShield Integration Audit & Architecture Document

## Executive Summary

This document details the architectural integration of the HeatShield: ShadeStop system, connecting the **Data Engineering & ML Pipeline**, the **FastAPI Analytics Backend**, and the **Next.js Frontend Dashboard** into a unified monorepo.

---

## 1. System Architecture & Data Flow

```
┌────────────────────────────────────────────────────────┐
│                   Data Engineering                     │
│  FortyGuard APIs + ACS Census + Satellite + GTFS Data  │
└───────────────────────────┬────────────────────────────┘
                            │
              data/processed/ & data/fixtures/
       (hartford_priority_scores.geojson & hartford_demo.json)
                            │
┌───────────────────────────▼────────────────────────────┐
│                    FastAPI Backend                     │
│    Exceedance/Persistence Scoring + Simulation Engine  │
└───────────────────────────┬────────────────────────────┘
                            │ REST APIs
┌───────────────────────────▼────────────────────────────┐
│                    Next.js Frontend                    │
│    Interactive Map + Table + Simulator + NL Box        │
└────────────────────────────────────────────────────────┘
```

---

## 2. API Contract & Endpoints

| Endpoint | Method | Description | Response Shape |
|----------|--------|-------------|----------------|
| `/health` | GET | Service status & version | `{"status": "ok", "data_mode": "fixture"}` |
| `/api/v1/cities` | GET | Hartford metadata & bounding box | `[{"id": "hartford-ct", "name": "Hartford", ...}]` |
| `/api/v1/analysis` | POST | Create/re-run heat analysis | `{"analysis_id": "...", "status": "completed"}` |
| `/api/v1/analyses/{id}/rankings` | GET | Ranked list of bus stops with custom weights support | `Array<RankingItem>` |
| `/api/v1/analyses/{id}/map-data` | GET | GeoJSON FeatureCollection for MapLibre rendering | `{"type": "FeatureCollection", ...}` |
| `/api/v1/assets/{id}` | GET | Stop detail: heat, shade, vulnerability, transit | `AssetDetails` |
| `/api/v1/assets/{id}/timeseries` | GET | Hourly temperature observations | `Array<{timestamp, value}>` |
| `/api/v1/interventions/simulate` | POST | Shade structure impact projection | `InterventionResponse` |
| `/api/v1/explanations` | POST | Grounded natural language explanations | `{"explanation": "..."}` |
| `/api/v1/reports/{id}` | GET | CSV download & report metadata | CSV text stream / JSON |

---

## 3. Key Integration Decisions

1. **Backend Ownership of Logic**: All priority scoring (40% heat, 25% shade, 20% vulnerability, 15% transit), exceedance degree-hour calculations, heat persistence durations, and intervention simulations are computed on the FastAPI backend.
2. **Standardized Frontend API Client**: The Next.js frontend calls the FastAPI backend via `NEXT_PUBLIC_API_BASE_URL` (`http://localhost:8000`), avoiding any self-mocking or direct external API key exposure.
3. **Fixture-First Reliability**: Demonstrations run in `DATA_MODE=fixture` with precomputed Hartford heat observations, ensuring fast, deterministic performance without depending on external API rate limits.
4. **Grounded Explanations**: Natural language planning answers are derived strictly from structured backend data and rule-based evidence.

---

## 4. Local Execution Commands

### Terminal 1: FastAPI Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Next.js Frontend
```bash
cd frontend
npm install
npm run dev
```

Dashboard is accessible at: **http://localhost:3000**
Interactive API docs at: **http://localhost:8000/docs**
