"""
Deterministic Priority Scoring and Percentile Normalization Engine.
Implements exact PRD & TRD algorithms for Heat, Shade, Vulnerability, Transit, and Final Priority.
"""

from typing import List, Dict, Any
import numpy as np
import pandas as pd

DEFAULT_WEIGHTS = {
    "heat": 0.40,
    "shade": 0.25,
    "vulnerability": 0.20,
    "transit": 0.15
}

def to_percentile_ranks(series: pd.Series) -> pd.Series:
    """Normalize a pandas numeric series to 0-100 percentile rank scale."""
    if len(series) <= 1:
        return pd.Series([50.0] * len(series), index=series.index)
    ranks = series.rank(method="min", ascending=True)
    min_r, max_r = ranks.min(), ranks.max()
    if max_r == min_r:
        return pd.Series([50.0] * len(series), index=series.index)
    return ((ranks - min_r) / (max_r - min_r)) * 100.0

def calculate_dataset_priority_scores(
    stops_df: pd.DataFrame,
    weights: Dict[str, float] = None
) -> pd.DataFrame:
    """
    Calculate normalized component scores and final priority scores for all Hartford bus stops.
    Returns DataFrame populated with component scores, final_score, rank, and priority_category.
    """
    w = weights or DEFAULT_WEIGHTS
    df = stops_df.copy()

    # Calculate component percentiles across all stops
    exceedance_pct = to_percentile_ranks(df["cumulative_exceedance"])
    duration_pct = to_percentile_ranks(df["dangerous_minutes"])
    persistence_pct = to_percentile_ranks(df["persistence_minutes"])

    # Composite Heat Score (50% Exceedance, 30% Duration, 20% Persistence)
    df["heat_score"] = np.round(
        0.50 * exceedance_pct + 0.30 * duration_pct + 0.20 * persistence_pct, 1
    )

    # Component Percentiles
    df["shade_score"] = np.round(to_percentile_ranks(df["shade_deficit"]), 1)
    df["vulnerability_score"] = np.round(to_percentile_ranks(df["raw_vulnerability_score"]), 1)
    
    # Transit importance metric (ridership * route_count)
    transit_importance = df["ridership"] * df["route_count"]
    df["transit_score"] = np.round(to_percentile_ranks(transit_importance), 1)

    # Final Priority Score
    raw_priority = (
        w["heat"] * df["heat_score"]
        + w["shade"] * df["shade_score"]
        + w["vulnerability"] * df["vulnerability_score"]
        + w["transit"] * df["transit_score"]
    )
    df["priority_score"] = np.round(raw_priority, 1)

    # Sort & Rank (Rank 1 is highest priority score)
    df = df.sort_values(by="priority_score", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1

    # Priority Categories
    def assign_category(score: float) -> str:
        if score >= 80.0:
            return "Critical"
        elif score >= 60.0:
            return "High"
        elif score >= 40.0:
            return "Moderate"
        else:
            return "Low"

    df["priority_category"] = df["priority_score"].apply(assign_category)
    return df
