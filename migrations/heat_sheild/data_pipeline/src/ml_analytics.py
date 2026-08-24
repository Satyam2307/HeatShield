"""
Optional ML & Geospatial Analytics Modules:
1. Persistence Anomaly Detection: Detects stops experiencing unusually high heat persistence relative to nearby geographic neighbors.
2. Sensitivity Analysis: Evaluates ranking stability across varying component weight combinations.
"""

from typing import Dict, List, Any
import numpy as np
import pandas as pd

def detect_persistence_anomalies(df: pd.DataFrame, z_threshold: float = 1.0) -> pd.DataFrame:
    """
    Identifies microclimate heat anomalies where a bus stop exhibits significantly higher
    persistence minutes than its local corridor neighbors.
    """
    df_out = df.copy()
    corridor_stats = df_out.groupby("corridor")["persistence_minutes"].transform(lambda x: (x - x.mean()) / (x.std() + 1e-6))
    df_out["persistence_z_score"] = np.round(corridor_stats, 2)
    df_out["is_heat_anomaly"] = df_out["persistence_z_score"] > z_threshold
    return df_out

def run_sensitivity_analysis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Tests ranking variance when weighting emphasis shifts towards Heat (60%) vs Vulnerability (40%).
    """
    from .scoring import calculate_priority_scores

    base_scored = calculate_priority_scores(df, weights={"heat": 0.40, "shade": 0.25, "vulnerability": 0.20, "transit": 0.15})
    heat_heavy = calculate_priority_scores(df, weights={"heat": 0.60, "shade": 0.15, "vulnerability": 0.15, "transit": 0.10})
    vuln_heavy = calculate_priority_scores(df, weights={"heat": 0.25, "shade": 0.20, "vulnerability": 0.45, "transit": 0.10})

    base_top10 = set(base_scored.head(10)["asset_id"])
    heat_top10 = set(heat_heavy.head(10)["asset_id"])
    vuln_top10 = set(vuln_heavy.head(10)["asset_id"])

    heat_overlap = len(base_top10.intersection(heat_top10)) / max(1, len(base_top10))
    vuln_overlap = len(base_top10.intersection(vuln_top10)) / max(1, len(base_top10))

    return {
        "heat_heavy_top10_overlap": heat_overlap,
        "vuln_heavy_top10_overlap": vuln_overlap,
        "ranking_stability": "High" if (heat_overlap >= 0.70 and vuln_overlap >= 0.70) else "Moderate"
    }
