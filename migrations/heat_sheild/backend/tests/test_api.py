"""
Integration tests for FastAPI backend endpoints.
"""

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["city"] == "Hartford, CT"

def test_get_cities():
    res = client.get("/api/v1/cities")
    assert res.status_code == 200
    cities = res.json()
    assert len(cities) == 1
    assert cities[0]["id"] == "hartford-ct"

def test_get_rankings():
    res = client.get("/api/v1/analyses/hartford-demo/rankings")
    assert res.status_code == 200
    data = res.json()
    assert "rankings" in data
    assert data["total_stops"] > 0
    top_stop = data["rankings"][0]
    assert top_stop["rank"] == 1
    assert "priority_score" in top_stop

def test_get_map_data():
    res = client.get("/api/v1/analyses/hartford-demo/map-data")
    assert res.status_code == 200
    geojson = res.json()
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) > 0

def test_simulate_intervention():
    # Fetch top stop ID
    rank_res = client.get("/api/v1/analyses/hartford-demo/rankings")
    top_asset_id = rank_res.json()["rankings"][0]["asset_id"]
    
    sim_res = client.post(
        "/api/v1/interventions/simulate",
        json={
            "analysis_id": "hartford-demo",
            "asset_id": top_asset_id,
            "intervention_type": "shade_structure",
            "scenario": "moderate"
        }
    )
    assert sim_res.status_code == 200
    sim_data = sim_res.json()
    assert sim_data["asset_id"] == top_asset_id
    assert sim_data["avoided_dangerous_minutes"] > 0
    assert sim_data["projected_rank"] >= 1

def test_explanation_endpoint():
    rank_res = client.get("/api/v1/analyses/hartford-demo/rankings")
    top_asset_id = rank_res.json()["rankings"][0]["asset_id"]
    
    exp_res = client.post(
        "/api/v1/explanations",
        json={"analysis_id": "hartford-demo", "asset_id": top_asset_id}
    )
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert "summary_explanation" in exp_data
    assert len(exp_data["key_drivers"]) > 0

def test_csv_report_export():
    rep_res = client.get("/api/v1/reports/hartford-demo")
    assert rep_res.status_code == 200
    assert "text/csv" in rep_res.headers["content-type"]
    assert "Rank,Asset ID,Stop Name" in rep_res.text
