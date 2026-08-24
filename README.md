# HeatShield: ShadeStop

**Which Hartford bus stops should receive shade first, and why?**

HeatShield: ShadeStop helps cities identify which bus stops should receive shade first by analyzing persistent heat exposure, shade deficit, community vulnerability, and transit importance.

## 🎯 What It Does

Converts **Heat data + Satellite data + Transit data + Census data** into a **ranked list of recommended bus-stop interventions** with measurable before/after results.

### The Wow Moment

Select the highest-priority bus stop and see:

```
Before shade:
  - 540 dangerous minutes
  - Priority score: 88.79
  - Rank: #1

After moderate shade scenario:
  - 389 dangerous minutes
  - Estimated reduction: 28%
  - Projected score: 67.09
  - New rank: #22
```

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│           Frontend (WIP)            │
│ Next.js + TypeScript + MapLibre     │
└────────────────┬────────────────────┘
                 │ REST/JSON
┌────────────────▼────────────────────┐
│           Backend (FastAPI)          │
│ Analytics + Scoring + Simulation    │
└────────────┬──────────────┬─────────┘
             │              │
   ┌─────────▼──────┐ ┌────▼──────────┐
   │ PostgreSQL     │ │ Fixture Data   │
   │ + PostGIS      │ │ JSON/GeoJSON   │
   └────────────────┘ └────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### Setup

```bash
# Clone and navigate
cd HeatShield

# Install dependencies
pip install -r backend/requirements.txt

# Create env file
cp .env.example .env

# Generate fixture data
python pipeline/scripts/generate_fixtures.py

# Start the API server
cd backend && uvicorn app.main:app --reload --port 8000
```

### Verify

```bash
# Health check
curl http://localhost:8000/health

# List cities
curl http://localhost:8000/api/v1/cities

# Run analysis
curl -X POST http://localhost:8000/api/v1/analysis

# Get rankings
curl http://localhost:8000/api/v1/analyses/fixture-001/rankings?limit=10

# Simulate shade intervention on top stop
curl -X POST http://localhost:8000/api/v1/interventions/simulate \
  -H "Content-Type: application/json" \
  -d '{"analysis_id":"fixture-001","asset_id":"stop-0149","scenario":"moderate"}'
```

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health check |
| GET | `/api/v1/cities` | List available cities |
| POST | `/api/v1/analysis` | Create heat analysis |
| GET | `/api/v1/analyses/{id}` | Get analysis status |
| GET | `/api/v1/analyses/{id}/rankings` | Ranked bus stops |
| GET | `/api/v1/analyses/{id}/map-data` | GeoJSON for map |
| GET | `/api/v1/assets/{id}` | Full stop detail |
| GET | `/api/v1/assets/{id}/timeseries` | Heat time-series |
| POST | `/api/v1/interventions/simulate` | Shade simulation |
| POST | `/api/v1/explanations` | Why is this stop ranked? |
| GET | `/api/v1/reports/{id}` | CSV/JSON report |

Interactive API docs: http://localhost:8000/docs

## 📊 Scoring Formula

```
Priority Score =
  40% × Heat Score
+ 25% × Shade Score
+ 20% × Vulnerability Score
+ 15% × Transit Score

Heat Score =
  50% × Cumulative Exceedance (percentile)
+ 30% × Dangerous Minutes (percentile)
+ 20% × Persistence (percentile)
```

### Priority Categories
| Score | Category |
|-------|----------|
| 80–100 | 🔴 Critical |
| 60–79 | 🟠 High |
| 40–59 | 🟡 Moderate |
| 0–39 | 🟢 Low |

## 🧪 Testing

```bash
cd backend && python -m pytest tests/ -v
```

56 tests covering:
- Exceedance calculations
- Persistence analysis
- Score normalization
- Priority ranking
- Intervention simulation
- Geospatial operations
- All API endpoints

## 📁 Project Structure

```
HeatShield/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── api/                 # Route handlers
│   │   ├── schemas/             # Pydantic models
│   │   ├── scoring/             # Analytics engine
│   │   ├── geospatial/          # Spatial utilities
│   │   ├── providers/           # External adapters
│   │   ├── services/            # Business logic
│   │   └── cache/               # File-based cache
│   └── tests/                   # 56 tests
├── pipeline/
│   └── scripts/
│       └── generate_fixtures.py # Data generator
├── data/
│   ├── boundaries/              # Hartford GeoJSON
│   ├── fixtures/                # Precomputed data
│   └── processed/               # MVP deliverables
├── docs/
│   ├── PRD.md
│   └── TRD.md
└── .env.example
```

## 🔧 Data Mode

Set `DATA_MODE=fixture` (default) to use precomputed Hartford data — no external API calls needed.

Set `DATA_MODE=live` to query FortyGuard, Census, and satellite APIs (requires API keys).

## 📄 License

MIT
