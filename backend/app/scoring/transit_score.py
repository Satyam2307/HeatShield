"""
Transit importance score calculation.

Uses ridership if available; falls back to proxies (route count, population).
Every value is labelled as observed, estimated, or proxy.
"""

from __future__ import annotations




def calculate_transit_score(
    route_count: int | None = None,
    ridership: float | None = None,
    nearby_population: float | None = None,
    service_frequency: str | None = None,
    nearby_essential_services: int | None = None,
) -> tuple[float, str]:
    """
    Calculate raw transit importance score (0–100) and data type label.

    Returns:
        (score, data_type) where data_type is 'observed', 'estimated', or 'proxy'.
    """
    # Use ridership if available (observed data)
    if ridership is not None and ridership > 0:
        # Normalize ridership: assume max ~2000 daily boardings
        score = min(100.0, (ridership / 2000.0) * 100)
        return round(score, 2), "observed"

    # Fallback to proxy combination
    components: list[tuple[float, float]] = []

    if route_count is not None:
        # Normalize: 1 route = low, 6+ = high
        route_norm = min(1.0, route_count / 6.0)
        components.append((0.50, route_norm))

    if nearby_population is not None:
        # Normalize: assume max ~5000 within walking distance
        pop_norm = min(1.0, nearby_population / 5000.0)
        components.append((0.25, pop_norm))

    if service_frequency is not None:
        freq_map = {"high": 1.0, "medium": 0.6, "low": 0.3}
        components.append((0.15, freq_map.get(service_frequency, 0.5)))

    if nearby_essential_services is not None:
        svc_norm = min(1.0, nearby_essential_services / 5.0)
        components.append((0.10, svc_norm))

    if not components:
        return 50.0, "proxy"

    total_weight = sum(w for w, _ in components)
    score = sum(w * v for w, v in components) / total_weight * 100

    return round(score, 2), "proxy"


def calculate_transit_scores(
    transit_data: list[dict],
) -> list[tuple[float, str]]:
    """
    Calculate transit scores for all stops.

    Returns list of (score, data_type) tuples.
    """
    return [
        calculate_transit_score(
            route_count=t.get("route_count"),
            ridership=t.get("ridership"),
            nearby_population=t.get("nearby_population"),
            service_frequency=t.get("service_frequency"),
            nearby_essential_services=t.get("nearby_essential_services"),
        )
        for t in transit_data
    ]


def percentile_normalize_transit(raw_scores: list[float]) -> list[float]:
    """Percentile-normalize transit scores to 0–100."""
    if not raw_scores:
        return []

    n = len(raw_scores)
    if n == 1:
        return [50.0]
    if all(s == raw_scores[0] for s in raw_scores):
        return [50.0] * n

    indexed = sorted(enumerate(raw_scores), key=lambda x: x[1])
    ranks = [0.0] * n
    for rank_pos, (orig_idx, _) in enumerate(indexed):
        ranks[orig_idx] = rank_pos + 1

    percentiles = [round(((r - 1) / (n - 1)) * 100.0, 2) for r in ranks]
    return percentiles
