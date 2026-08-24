"""
Final priority score calculation.

Combines heat, shade, vulnerability, and transit component scores
into a weighted final priority score with ranking and categorization.
"""

from __future__ import annotations

from app.config import settings


def categorize_priority(score: float) -> str:
    """Assign a priority category based on the final score."""
    if score >= 80:
        return "Critical"
    elif score >= 60:
        return "High"
    elif score >= 40:
        return "Moderate"
    else:
        return "Low"


def calculate_priority_scores(
    heat_scores: list[float],
    shade_scores: list[float],
    vulnerability_scores: list[float],
    transit_scores: list[float],
    weights: dict[str, float] | None = None,
) -> list[dict]:
    """
    Calculate final priority scores for all stops.

    Args:
        heat_scores: Percentile-normalized heat scores (0–100).
        shade_scores: Percentile-normalized shade scores (0–100).
        vulnerability_scores: Percentile-normalized vulnerability scores (0–100).
        transit_scores: Percentile-normalized transit scores (0–100).
        weights: Optional weight overrides {heat, shade, vulnerability, transit}.

    Returns:
        List of dicts with final_score, rank, and priority_category.
    """
    w = weights or {
        "heat": settings.scoring_weights.heat,
        "shade": settings.scoring_weights.shade,
        "vulnerability": settings.scoring_weights.vulnerability,
        "transit": settings.scoring_weights.transit,
    }

    n = len(heat_scores)
    results: list[dict] = []

    for i in range(n):
        final = (
            w["heat"] * heat_scores[i]
            + w["shade"] * shade_scores[i]
            + w["vulnerability"] * vulnerability_scores[i]
            + w["transit"] * transit_scores[i]
        )
        final = round(final, 2)

        results.append({
            "heat_score": heat_scores[i],
            "shade_score": shade_scores[i],
            "vulnerability_score": vulnerability_scores[i],
            "transit_score": transit_scores[i],
            "final_score": final,
            "priority_category": categorize_priority(final),
            "scoring_version": settings.scoring_version,
        })

    # Rank by final_score descending (rank 1 = highest priority)
    sorted_indices = sorted(range(n), key=lambda i: results[i]["final_score"], reverse=True)
    for rank, idx in enumerate(sorted_indices, start=1):
        results[idx]["rank"] = rank

    return results
