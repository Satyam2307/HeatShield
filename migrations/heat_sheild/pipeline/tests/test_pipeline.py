"""
Unit tests for HeatShield pipeline components:
- Exceedance calculation
- Persistence calculation
- Percentile normalization
- Priority scoring
- Intervention simulator
"""

import pytest
import pandas as pd
import numpy as np
from pipeline.src.fortyguard import calculate_stop_heat_metrics
from pipeline.src.scoring import to_percentile_ranks, calculate_dataset_priority_scores
from pipeline.src.simulator import simulate_stop_intervention

def test_exceedance_and_persistence_calculation():
    # Observations where heat index is above 95°F for 3 consecutive hours (hours 13, 14, 15)
    obs = [
        {"hour": 10, "heat_index": 92.0},
        {"hour": 11, "heat_index": 94.0},
        {"hour": 12, "heat_index": 94.5},
        {"hour": 13, "heat_index": 96.0}, # +1.0 exceedance
        {"hour": 14, "heat_index": 98.0}, # +3.0 exceedance
        {"hour": 15, "heat_index": 97.0}, # +2.0 exceedance
        {"hour": 16, "heat_index": 93.0},
        {"hour": 17, "heat_index": 91.0},
        {"hour": 18, "heat_index": 89.0}
    ]
    
    metrics = calculate_stop_heat_metrics(obs, danger_threshold=95.0, interval_hours=1.0)
    
    assert metrics["cumulative_exceedance"] == 6.0  # 1 + 3 + 2
    assert metrics["dangerous_intervals"] == 3
    assert metrics["dangerous_minutes"] == 180.0
    assert metrics["persistence_minutes"] == 180.0
    assert metrics["peak_hour"] == 14
    assert metrics["maximum_heat"] == 98.0

def test_percentile_ranks():
    s = pd.Series([10.0, 20.0, 30.0, 40.0, 50.0])
    pct = to_percentile_ranks(s)
    assert pct.iloc[0] == 0.0
    assert pct.iloc[-1] == 100.0
    assert pct.iloc[2] == 50.0

def test_intervention_simulator():
    stop = {
        "asset_id": "stop-001",
        "name": "Main St Test Stop",
        "dangerous_minutes": 240.0,
        "cumulative_exceedance": 12.0,
        "persistence_minutes": 180.0,
        "priority_score": 86.0,
        "rank": 1,
        "components": {
            "heat": 90.0,
            "shade": 85.0,
            "vulnerability": 80.0,
            "transit": 70.0
        }
    }
    all_stops = [
        stop,
        {"asset_id": "stop-002", "priority_score": 82.0},
        {"asset_id": "stop-003", "priority_score": 78.0},
        {"asset_id": "stop-004", "priority_score": 75.0}
    ]
    
    res = simulate_stop_intervention(stop, all_stops, scenario="moderate")
    
    assert res["avoided_dangerous_minutes"] == 84.0 # 35% of 240
    assert res["projected_dangerous_minutes"] == 156.0 # 240 - 84
    assert res["projected_priority_score"] < 86.0
    assert res["projected_rank"] > 1
    assert res["rank_change"] > 0
