"""
Heat score calculation.

Combines exceedance, dangerous duration, and persistence into a single
composite heat score using percentile-based normalization.
"""

from __future__ import annotations

import numpy as np

from app.config import settings


def percentile_normalize(values: list[float]) -> list[float]:
    """
    Normalize values to 0–100 using percentile ranking.

    Each value is replaced by its percentile rank within the array.
    Ties get the average of their ranks.
    """
    if not values:
        return []

    arr = np.array(values, dtype=float)
    n = len(arr)

    if n == 1:
        return [50.0]

    # Handle case where all values are identical
    if np.all(arr == arr[0]):
        return [50.0] * n

    # Rank-based percentile using numpy only (no scipy dependency)
    sorted_indices = np.argsort(arr)
    ranks = np.empty(n, dtype=float)
    for rank_pos, idx in enumerate(sorted_indices):
        ranks[idx] = rank_pos + 1

    # Convert ranks to percentiles (0–100)
    percentiles = ((ranks - 1) / (n - 1)) * 100.0
    return [round(float(p), 2) for p in percentiles]


def calculate_heat_scores(
    cumulative_exceedances: list[float],
    dangerous_minutes_list: list[float],
    persistence_minutes_list: list[float],
    weights: dict[str, float] | None = None,
) -> list[dict]:
    """
    Calculate composite heat scores for all stops.

    Each component is percentile-normalized, then combined using weights.

    Args:
        cumulative_exceedances: Per-stop cumulative exceedance values.
        dangerous_minutes_list: Per-stop total dangerous minutes.
        persistence_minutes_list: Per-stop longest persistence minutes.
        weights: Optional weight overrides.

    Returns:
        List of dicts with heat_score and sub-component percentiles.
    """
    w = weights or {
        "cumulative_exceedance": settings.scoring_weights.heat_cumulative_exceedance,
        "dangerous_minutes": settings.scoring_weights.heat_dangerous_minutes,
        "persistence": settings.scoring_weights.heat_persistence,
    }

    # Percentile-normalize each component
    ce_pct = percentile_normalize(cumulative_exceedances)
    dm_pct = percentile_normalize(dangerous_minutes_list)
    pm_pct = percentile_normalize(persistence_minutes_list)

    results = []
    for i in range(len(cumulative_exceedances)):
        score = (
            w["cumulative_exceedance"] * ce_pct[i]
            + w["dangerous_minutes"] * dm_pct[i]
            + w["persistence"] * pm_pct[i]
        )
        results.append({
            "heat_score": round(score, 2),
            "cumulative_exceedance_percentile": ce_pct[i],
            "dangerous_minutes_percentile": dm_pct[i],
            "persistence_percentile": pm_pct[i],
        })

    return results
