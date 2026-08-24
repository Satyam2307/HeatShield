"""
Deterministic Priority Scoring Engine for Hartford Bus Stops.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd

DEFAULT_WEIGHTS = {
    "heat": 0.40,
    "shade": 0.25,
    "vulnerability": 0.20,
    "transit": 0.15
}

def to_percentile_ranks(series: pd.Series) -> pd.Series:
    if len(series) <= 1:
        return pd.Series([50.0] * len(series), index=series.index)
    ranks = series.rank(method="min", ascending=True)
    min_r, max_r = ranks.min(), ranks.max()
    if max_r == min_r:
        return pd.Series([50.0] * len(series), index=series.index)
    return ((ranks - min_r) / (max_r - min_r)) * 100.0

def calculate_priority_scores(df: pd.DataFrame, weights: Dict[str, float] = None) -> pd.DataFrame:
    w = weights or DEFAULT_WEIGHTS
    df_out = df.copy()

    exceedance_pct = to_percentile_ranks(df_out["cumulative_exceedance"])
    duration_pct = to_percentile_ranks(df_out["dangerous_minutes"])
    persistence_pct = to_percentile_ranks(df_out["persistence_minutes"])

    df_out["heat_score"] = np.round(
        0.50 * exceedance_pct + 0.30 * duration_pct + 0.20 * persistence_pct, 1
    )
    df_out["shade_score"] = np.round(to_percentile_ranks(df_out["shade_deficit"]), 1)
    df_out["vulnerability_score"] = np.round(to_percentile_ranks(df_out["raw_vulnerability_score"]), 1)
    
    transit_importance = df_out["ridership"] * df_out["route_count"]
    df_out["transit_score"] = np.round(to_percentile_ranks(transit_importance), 1)

    raw_priority = (
        w["heat"] * df_out["heat_score"]
        + w["shade"] * df_out["shade_score"]
        + w["vulnerability"] * df_out["vulnerability_score"]
        + w["transit"] * df_out["transit_score"]
    )
    df_out["priority_score"] = np.round(raw_priority, 1)

    df_out = df_out.sort_values(by="priority_score", ascending=False).reset_index(drop=True)
    df_out["rank"] = df_out.index + 1

    def assign_category(score: float) -> str:
        if score >= 80.0:
            return "Critical"
        elif score >= 60.0:
            return "High"
        elif score >= 40.0:
            return "Moderate"
        else:
            return "Low"

    df_out["priority_category"] = df_out["priority_score"].apply(assign_category)
    return df_out
