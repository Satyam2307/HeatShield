"""
Explanation service for generating natural language evidence cards based on backend values.
"""

from typing import Dict, Any

def generate_stop_explanation(stop_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construct evidence-based natural language explanation for a ranked bus stop.
    """
    name = stop_data.get("name", "Bus Stop")
    rank = stop_data.get("rank", 0)
    score = stop_data.get("priority_score", 0.0)
    category = stop_data.get("priority_category", "Moderate")
    
    metrics = stop_data.get("metrics", {})
    danger_mins = metrics.get("dangerous_minutes", 0)
    persistence = metrics.get("persistence_minutes", 0)
    peak_hour = metrics.get("peak_hour", 15)
    
    shade = stop_data.get("shade_details", {})
    shade_deficit = int(shade.get("shade_deficit", 0) * 100)
    shelter = shade.get("shelter_status", "No Shelter")
    
    vuln = stop_data.get("vulnerability_details", {})
    neighborhood = vuln.get("neighborhood_name", "Hartford")
    zero_veh = int(vuln.get("zero_vehicle_fraction", 0) * 100)
    
    transit = stop_data.get("transit_details", {})
    routes_cnt = transit.get("route_count", 0)
    
    peak_ampm = f"{peak_hour - 12} PM" if peak_hour > 12 else (f"{peak_hour} AM" if peak_hour < 12 else "12 PM")

    explanation_text = (
        f"This bus stop ({name}) ranks #{rank} in Hartford with a {category} Priority Score of {score}/100. "
        f"It experiences persistent afternoon heat exposure, staying above dangerous thresholds for {int(danger_mins)} minutes "
        f"(with a peak heat index reached at {peak_ampm}). It currently has an estimated {shade_deficit}% shade deficit "
        f"({shelter}), serves the {neighborhood} neighborhood where {zero_veh}% of households lack a personal vehicle, "
        f"and connects riders across {routes_cnt} CTtransit routes."
    )

    key_drivers = [
        f"Heat Exposure: {int(danger_mins)} dangerous minutes ({int(persistence)} min longest continuous event)",
        f"Peak Heat Window: Reaches daily maximum at {peak_ampm}",
        f"Shade Deficit: {shade_deficit}% estimated deficit ({shelter})",
        f"Equity & Transit: {neighborhood} ({zero_veh}% zero-vehicle households), {routes_cnt} transit routes"
    ]

    return {
        "asset_id": stop_data.get("asset_id"),
        "rank": rank,
        "priority_score": score,
        "priority_category": category,
        "summary_explanation": explanation_text,
        "key_drivers": key_drivers,
        "structured_evidence": {
            "dangerous_minutes": danger_mins,
            "persistence_minutes": persistence,
            "peak_hour": peak_hour,
            "shade_deficit": shade.get("shade_deficit"),
            "zero_vehicle_pct": zero_veh,
            "route_count": routes_cnt
        }
    }
