"""Tests for scoring modules."""

from app.scoring.heat_score import percentile_normalize, calculate_heat_scores
from app.scoring.shade_score import calculate_shade_deficit, calculate_shade_scores
from app.scoring.vulnerability_score import calculate_vulnerability_score
from app.scoring.transit_score import calculate_transit_score
from app.scoring.priority import calculate_priority_scores, categorize_priority


# --- Percentile normalization ---

def test_percentile_normalize_basic():
    result = percentile_normalize([10.0, 20.0, 30.0])
    assert result == [0.0, 50.0, 100.0]


def test_percentile_normalize_single():
    result = percentile_normalize([42.0])
    assert result == [50.0]


def test_percentile_normalize_identical():
    result = percentile_normalize([5.0, 5.0, 5.0])
    assert result == [50.0, 50.0, 50.0]


def test_percentile_normalize_empty():
    result = percentile_normalize([])
    assert result == []


# --- Heat score ---

def test_heat_scores():
    results = calculate_heat_scores(
        cumulative_exceedances=[10.0, 20.0, 30.0],
        dangerous_minutes_list=[60.0, 120.0, 180.0],
        persistence_minutes_list=[30.0, 60.0, 90.0],
    )
    assert len(results) == 3
    # Third stop should have highest score (100 percentile for all components)
    assert results[2]["heat_score"] == 100.0
    # First stop should have lowest score (0 percentile)
    assert results[0]["heat_score"] == 0.0


# --- Shade deficit ---

def test_shade_deficit_high():
    # No vegetation, no building, no shelter = high deficit
    deficit = calculate_shade_deficit(0.0, 0.8, 0.0, 0.0, "absent")
    assert deficit >= 0.9


def test_shade_deficit_low_with_shelter():
    # Good vegetation + shelter = low deficit
    deficit = calculate_shade_deficit(0.6, 0.2, 0.1, 0.4, "present")
    assert deficit <= 0.3


def test_shade_scores_ranking():
    deficits = [0.2, 0.8, 0.5]
    scores = calculate_shade_scores(deficits)
    # 0.8 should get highest score (most need for intervention)
    assert scores[1] == 100.0
    assert scores[0] == 0.0


# --- Vulnerability ---

def test_vulnerability_score_high():
    score = calculate_vulnerability_score(
        zero_vehicle_fraction=0.45,
        older_adult_fraction=0.25,
        children_fraction=0.30,
        median_income=22000,
        population_density=10000,
    )
    assert score > 70


def test_vulnerability_score_low():
    score = calculate_vulnerability_score(
        zero_vehicle_fraction=0.05,
        older_adult_fraction=0.08,
        children_fraction=0.15,
        median_income=85000,
        population_density=2000,
    )
    assert score < 30


def test_vulnerability_missing_data():
    # Should return default when no data
    score = calculate_vulnerability_score(None, None, None, None, None)
    assert score == 50.0


# --- Transit score ---

def test_transit_score_with_ridership():
    score, dtype = calculate_transit_score(ridership=1500)
    assert dtype == "observed"
    assert score > 50


def test_transit_score_with_proxies():
    score, dtype = calculate_transit_score(route_count=4)
    assert dtype == "proxy"
    assert score > 0


def test_transit_score_empty():
    score, dtype = calculate_transit_score()
    assert dtype == "proxy"
    assert score == 50.0  # Default


# --- Priority score ---

def test_priority_scores():
    results = calculate_priority_scores(
        heat_scores=[80.0, 60.0, 40.0],
        shade_scores=[70.0, 50.0, 30.0],
        vulnerability_scores=[90.0, 60.0, 20.0],
        transit_scores=[60.0, 40.0, 80.0],
    )
    assert len(results) == 3
    # Check ranks are assigned
    ranks = {r["rank"] for r in results}
    assert ranks == {1, 2, 3}


def test_categorize_priority():
    assert categorize_priority(85) == "Critical"
    assert categorize_priority(70) == "High"
    assert categorize_priority(50) == "Moderate"
    assert categorize_priority(30) == "Low"
