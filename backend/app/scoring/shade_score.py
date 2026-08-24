"""
Shade deficit score calculation.

Uses satellite/land-cover data as a PROXY for shade conditions.
Higher shade deficit = less shade = higher priority.
"""

from __future__ import annotations

import numpy as np


def calculate_shade_deficit(
    vegetation_fraction: float | None,
    impervious_fraction: float | None,
    building_fraction: float | None,
    canopy_fraction: float | None = None,
    shelter_status: str | None = None,
) -> float:
    """
    Estimate shade deficit from land-cover fractions.

    Shade deficit = 1.0 means no shade (worst case).
    Shade deficit = 0.0 means full shade (best case).

    Logic:
        - Vegetation and canopy provide shade
        - Buildings provide partial shade (shadows)
        - Existing shelter reduces deficit
        - Impervious surfaces increase heat but don't directly affect shade
    """
    veg = vegetation_fraction or 0.0
    canopy = canopy_fraction or (veg * 0.6)
    bld = building_fraction or 0.0

    # Base shade estimate: canopy and building shadow contribution
    shade_coverage = canopy + bld * 0.2

    # Shelter bonus
    if shelter_status == "present":
        shade_coverage += 0.3

    # Deficit is the complement, clamped to [0, 1]
    deficit = max(0.0, min(1.0, 1.0 - shade_coverage))
    return round(deficit, 3)


def calculate_shade_scores(shade_deficits: list[float]) -> list[float]:
    """
    Convert shade deficits to 0–100 scores.

    Higher deficit → higher score (more need for intervention).
    Uses percentile normalization for city-relative ranking.
    """
    if not shade_deficits:
        return []

    arr = np.array(shade_deficits, dtype=float)
    n = len(arr)

    if n == 1:
        return [round(float(arr[0]) * 100, 2)]

    if np.all(arr == arr[0]):
        return [50.0] * n

    # Percentile ranking
    sorted_indices = np.argsort(arr)
    ranks = np.empty(n, dtype=float)
    for rank_pos, idx in enumerate(sorted_indices):
        ranks[idx] = rank_pos + 1

    percentiles = ((ranks - 1) / (n - 1)) * 100.0
    return [round(float(p), 2) for p in percentiles]
