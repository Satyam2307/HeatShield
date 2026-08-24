"""API integration tests using FastAPI TestClient."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# --- Health ---

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "data_mode" in data


# --- Cities ---

def test_list_cities():
    r = client.get("/api/v1/cities")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == "hartford-ct"
    assert data[0]["name"] == "Hartford"
    assert len(data[0]["bbox"]) == 4


# --- Analysis ---

def test_create_analysis():
    r = client.post("/api/v1/analysis")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["total_stops"] == 150
    assert data["city_id"] == "hartford-ct"


def test_get_analysis():
    r = client.get("/api/v1/analyses/fixture-001")
    assert r.status_code == 200
    data = r.json()
    assert data["analysis_id"] == "fixture-001"


def test_get_rankings():
    r = client.get("/api/v1/analyses/fixture-001/rankings?limit=10")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 10
    # Verify sorted by rank
    ranks = [s["rank"] for s in data]
    assert ranks == sorted(ranks)
    # First stop should be rank 1
    assert data[0]["rank"] == 1


def test_get_map_data():
    r = client.get("/api/v1/analyses/fixture-001/map-data")
    assert r.status_code == 200
    data = r.json()
    assert data["type"] == "FeatureCollection"
    assert len(data["features"]) == 150


# --- Asset Detail ---

def test_get_asset_detail():
    # First get a valid stop ID
    rankings = client.get("/api/v1/analyses/fixture-001/rankings?limit=1").json()
    stop_id = rankings[0]["bus_stop_id"]

    r = client.get(f"/api/v1/assets/{stop_id}?analysis_id=fixture-001")
    assert r.status_code == 200
    data = r.json()
    assert "score_breakdown" in data
    assert "community_vulnerability" in data
    assert "transit_importance" in data
    assert "dangerous_minutes" in data


def test_get_asset_timeseries():
    rankings = client.get("/api/v1/analyses/fixture-001/rankings?limit=1").json()
    stop_id = rankings[0]["bus_stop_id"]

    r = client.get(f"/api/v1/assets/{stop_id}/timeseries?analysis_id=fixture-001")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 9


# --- Intervention ---

def test_simulate_intervention():
    rankings = client.get("/api/v1/analyses/fixture-001/rankings?limit=1").json()
    stop_id = rankings[0]["bus_stop_id"]

    r = client.post(
        "/api/v1/interventions/simulate",
        json={
            "analysis_id": "fixture-001",
            "asset_id": stop_id,
            "scenario": "moderate",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["projected_dangerous_minutes"] < data["baseline_dangerous_minutes"]
    assert data["exposure_reduction_pct"] > 0
    assert "assumptions" in data


# --- Explanation ---

def test_generate_explanation():
    rankings = client.get("/api/v1/analyses/fixture-001/rankings?limit=1").json()
    stop_id = rankings[0]["bus_stop_id"]

    r = client.post(
        "/api/v1/explanations",
        json={"analysis_id": "fixture-001", "asset_id": stop_id},
    )
    assert r.status_code == 200
    data = r.json()
    assert "explanation" in data


# --- Report ---

def test_csv_report():
    r = client.get("/api/v1/reports/fixture-001?format=csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
    assert "HeatShield" in r.text
    assert "Rank" in r.text


def test_json_report():
    r = client.get("/api/v1/reports/fixture-001?format=json")
    assert r.status_code == 200
    data = r.json()
    assert "metadata" in data
    assert data["metadata"]["city"] == "hartford-ct"

