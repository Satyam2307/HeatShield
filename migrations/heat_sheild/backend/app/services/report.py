"""
Report generation service to produce CSV export files for Hartford city planners.
"""

import io
import csv
from typing import List, Dict, Any

def generate_rankings_csv(rankings: List[Dict[str, Any]]) -> str:
    """Generate CSV string of prioritized bus stops for export."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Write Header
    writer.writerow([
        "Rank", "Asset ID", "Stop Name", "Corridor", "Neighborhood", "Priority Score", "Category",
        "Heat Score", "Shade Score", "Vulnerability Score", "Transit Score",
        "Dangerous Minutes", "Persistence Minutes", "Cumulative Exceedance (F*hr)", "Peak Hour",
        "Shelter Status", "Shade Deficit Pct", "Zero Vehicle Household Pct", "Route Count"
    ])

    for item in rankings:
        metrics = item.get("metrics", {})
        components = item.get("components", {})
        shade = item.get("shade_details", {})
        vuln = item.get("vulnerability_details", {})
        transit = item.get("transit_details", {})

        writer.writerow([
            item.get("rank"),
            item.get("asset_id"),
            item.get("name"),
            item.get("corridor"),
            vuln.get("neighborhood_name"),
            item.get("priority_score"),
            item.get("priority_category"),
            components.get("heat"),
            components.get("shade"),
            components.get("vulnerability"),
            components.get("transit"),
            metrics.get("dangerous_minutes"),
            metrics.get("persistence_minutes"),
            metrics.get("cumulative_exceedance"),
            metrics.get("peak_hour"),
            shade.get("shelter_status"),
            f"{int(shade.get('shade_deficit', 0) * 100)}%",
            f"{int(vuln.get('zero_vehicle_fraction', 0) * 100)}%",
            transit.get("route_count")
        ])

    return output.getvalue()
