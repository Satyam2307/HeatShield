# Data Engineering & Analytics Pipeline — HeatShield: ShadeStop (Hartford, CT)

Reproducible geospatial data engineering and analytics pipeline for **HeatShield: ShadeStop**, prioritizing Hartford bus stops for shade canopy interventions.

---

## 📁 Directory Structure

```text
data_pipeline/
├── config/
│   └── pipeline_config.yaml       # YAML configuration parameters
├── raw/                           # Raw ingested data cache
├── staging/                       # Intermediate spatial join staging
├── processed/                     # Production Parquet & GeoJSON outputs
├── manifests/                     # Data run quality reports (JSON)
├── src/
│   ├── boundaries.py              # Spatial boundary ingestion & clipping
│   ├── transit.py                 # GTFS bus stops & EPSG:3437 metric 100m buffers
│   ├── fortyguard.py              # FortyGuard heat index & time-series adapter
│   ├── census.py                   # US Census ACS 5-Year vulnerability indicators
│   ├── satellite.py               # Satellite land-cover proxy (vegetation, pavement)
│   ├── exposure.py                # Exceedance, persistence & peak-hour metrics
│   ├── scoring.py                 # Deterministic percentile priority ranking
│   ├── ml_analytics.py            # Persistence anomaly detection & sensitivity testing
│   └── quality.py                 # Run manifest & data quality reporting
├── notebooks/                     # Exploratory notebooks
├── tests/
│   └── test_data_pipeline.py      # Pytest test suite
└── run_pipeline.py                # Master execution pipeline script
```

---

## ⚡ Quick Start & Execution

### 1. Download Census Boundaries
```bash
python scripts/download_boundaries.py
```

### 2. Execute Data Pipeline
```bash
python data_pipeline/run_pipeline.py
```

### 3. Run Pipeline Test Suite
```bash
python -m pytest data_pipeline/tests/
```

---

## 📊 Processed Data Artifacts Generated

Running `run_pipeline.py` creates the following files in `data/processed/` and `data/fixtures/`:

1. `data/processed/hartford_bus_stops.parquet`
2. `data/processed/hartford_exposure_metrics.parquet`
3. `data/processed/hartford_shade_metrics.parquet`
4. `data/processed/hartford_vulnerability_metrics.parquet`
5. `data/processed/hartford_priority_scores.parquet`
6. `data/processed/hartford_priority_scores.geojson`
7. `data/fixtures/hartford_demo.json`
8. `data_pipeline/manifests/latest_run.json`

---

## 🌐 Coordinate Reference Systems (CRS)

- **EPSG:4326 (WGS84)**: Used for GeoJSON exchange, API requests, and web mapping.
- **EPSG:3437 (NAD83 / Connecticut State Plane)**: Used internally for metric 100-meter buffer calculations and spatial distance operations.
