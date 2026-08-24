"""
Explanation service — generates structured evidence and narrative explanations.

Explanations are built from computed data, never invented.
Optional LLM enhancement uses structured evidence as input.
"""

from __future__ import annotations

from app.config import settings


def generate_explanation(
    stop_data: dict,
    analysis_data: dict | None = None,
) -> dict:
    """
    Generate a structured explanation for a bus stop's priority ranking.

    Args:
        stop_data: Full stop data dict from analysis result.
        analysis_data: Optional analysis metadata.

    Returns:
        Explanation dict with evidence, reasons, and narrative.
    """
    score = stop_data.get("priority_score", 0)
    rank = stop_data.get("rank", 0)
    category = stop_data.get("priority_category", "Unknown")

    # Build recommendation reasons
    reasons = []

    # Heat-related reasons
    dang_min = stop_data.get("dangerous_minutes", 0)
    if dang_min >= 300:
        reasons.append(f"Experiences {int(dang_min)} dangerous minutes of heat exposure")
    elif dang_min >= 180:
        reasons.append(f"Experiences {int(dang_min)} minutes above the danger threshold")

    pers_min = stop_data.get("persistence_minutes", 0)
    if pers_min >= 180:
        reasons.append(f"Heat persists continuously for {int(pers_min)} minutes")
    elif pers_min >= 120:
        reasons.append(f"Sustained heat exposure lasting {int(pers_min)} minutes")

    peak_hour = stop_data.get("peak_hour")
    if peak_hour is not None:
        reasons.append(f"Reaches peak heat at approximately {peak_hour}:00")

    # Shade reasons
    shade_deficit = stop_data.get("shade_deficit", 0)
    if shade_deficit >= 0.7:
        reasons.append("Has very low estimated shade coverage")
    elif shade_deficit >= 0.5:
        reasons.append("Has limited estimated shade coverage")

    shelter = stop_data.get("shelter_status")
    if shelter == "absent":
        reasons.append("Currently has no shelter structure")

    # Vulnerability reasons
    vuln_metrics = stop_data.get("vulnerability_metrics", {})
    zvf = vuln_metrics.get("zero_vehicle_fraction", 0)
    if zvf and zvf >= 0.3:
        reasons.append(
            f"Serves an area where {int(zvf * 100)}% of households have no vehicle"
        )

    oaf = vuln_metrics.get("older_adult_fraction", 0)
    if oaf and oaf >= 0.2:
        reasons.append(f"Located near a higher concentration of older adults")

    income = vuln_metrics.get("median_income", 0)
    if income and income < 30000:
        reasons.append("Serves a lower-income community")

    # Transit reasons
    route_count = stop_data.get("route_count", 0)
    if route_count and route_count >= 4:
        reasons.append(f"Served by {route_count} transit routes")
    elif route_count and route_count >= 2:
        reasons.append(f"Served by {route_count} transit routes")

    # Default if no strong reasons
    if not reasons:
        reasons.append("Moderate heat exposure relative to other Hartford bus stops")

    # Build template explanation
    name = stop_data.get("name", f"Stop {stop_data.get('id', 'unknown')}")
    template = _build_template(name, rank, category, reasons, dang_min, pers_min, shade_deficit)

    return {
        "asset_id": stop_data.get("id", ""),
        "stop_name": name,
        "rank": rank,
        "priority_score": score,
        "priority_category": category,
        "recommendation_reasons": reasons,
        "score_components": {
            "heat_score": stop_data.get("heat_score", 0),
            "shade_score": stop_data.get("shade_score", 0),
            "vulnerability_score": stop_data.get("vulnerability_score", 0),
            "transit_score": stop_data.get("transit_score", 0),
        },
        "key_metrics": {
            "dangerous_minutes": dang_min,
            "persistence_minutes": pers_min,
            "cumulative_exceedance": stop_data.get("cumulative_exceedance", 0),
            "shade_deficit": shade_deficit,
            "peak_hour": peak_hour,
            "average_heat": stop_data.get("average_heat"),
            "maximum_heat": stop_data.get("maximum_heat"),
        },
        "sources": [
            "FortyGuard heat analytics (fixture)",
            "Satellite land-cover proxy (fixture)",
            "ACS 5-year 2022 Census estimates (fixture)",
            "CTtransit GTFS (fixture)",
        ],
        "assumptions": [
            "Heat values are based on a single historical day analysis",
            "Shade deficit is a proxy estimate from satellite land-cover data",
            "Community vulnerability indicators are from Census tract-level data",
            "Transit importance is based on route count (proxy)",
        ],
        "template_explanation": template,
        "ai_explanation": None,
        "methodology": (
            "Priority scores combine heat exposure (40%), shade deficit (25%), "
            "community vulnerability indicators (20%), and transit importance (15%). "
            "All component scores are percentile-normalized to 0–100."
        ),
    }


def _build_template(
    name: str,
    rank: int,
    category: str,
    reasons: list[str],
    dangerous_minutes: float,
    persistence_minutes: float,
    shade_deficit: float,
) -> str:
    """Build a deterministic narrative explanation from structured data."""
    lines = [f'"{name}" is ranked #{rank} ({category} priority).']

    if reasons:
        lines.append("This bus stop ranks highly because it:")
        for r in reasons[:5]:  # Limit to top 5 reasons
            lines.append(f"  • {r}")

    if dangerous_minutes > 0:
        hours = int(dangerous_minutes // 60)
        mins = int(dangerous_minutes % 60)
        if hours > 0:
            lines.append(
                f"\nDuring the analysis period, this stop experienced "
                f"{hours} hour(s) and {mins} minute(s) of dangerous heat conditions."
            )

    if shade_deficit >= 0.5:
        lines.append(
            "\nThe estimated shade deficit indicates limited natural or built shade coverage "
            "in the surrounding area."
        )

    lines.append(
        "\nAdding a shade structure at this location could meaningfully reduce "
        "heat exposure for transit riders."
    )

    return "\n".join(lines)
