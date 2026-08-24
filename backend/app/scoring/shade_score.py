"""
Shade deficit score calculation.

Uses satellite/land-cover data as a PROXY for shade conditions.
Higher shade deficit = less shade = higher priority.
"""

from __future__ import annotations

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
    """
    veg = vegetation_fraction or 0.0
    canopy = canopy_fraction or (veg * 0.6)
    bld = building_fraction or 0.0

    shade_coverage = canopy + bld * 0.2
    if shelter_status == "present":
        shade_coverage += 0.3

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

    n = len(shade_deficits)
    if n == 1:
        return [round(float(shade_deficits[0]) * 100, 2)]

    if all(d == shade_deficits[0] for d in shade_deficits):
        return [50.0] * n

    indexed = sorted(enumerate(shade_deficits), key=lambda x: x[1])
    ranks = [0.0] * n
    for rank_pos, (orig_idx, _) in enumerate(indexed):
        ranks[orig_idx] = rank_pos + 1

    percentiles = [round(((r - 1) / (n - 1)) * 100.0, 2) for r in ranks]
    return percentiles
