"""
Report service — CSV/PDF export of analysis results.

MVP: CSV export with full methodology and assumptions.
"""

from __future__ import annotations

import csv
import io
from datetime import datetime, timezone


def generate_csv_report(analysis: dict) -> str:
    """
    Generate a CSV report string from an analysis result.

    Includes:
        - Ranked bus stops with score breakdowns
        - Metadata header rows
        - Methodology and assumptions
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Metadata header
    writer.writerow(["# HeatShield: ShadeStop — Priority Report"])
    writer.writerow(["# City", analysis.get("city_id", "hartford-ct")])
    writer.writerow(["# Analysis Date", analysis.get("start_time", "").split("T")[0]])
    writer.writerow(["# Heat Metric", analysis.get("heat_metric", "")])
    writer.writerow(["# Danger Threshold", analysis.get("danger_threshold", "")])
    writer.writerow(["# Scoring Version", analysis.get("scoring_version", "")])
    writer.writerow(["# Generated At", datetime.now(timezone.utc).isoformat()])
    writer.writerow(["# Total Stops", analysis.get("total_stops", 0)])
    writer.writerow([])

    # Column headers
    headers = [
        "Rank",
        "Stop ID",
        "Stop Name",
        "Priority Score",
        "Priority Category",
        "Heat Score",
        "Shade Score",
        "Vulnerability Score",
        "Transit Score",
        "Dangerous Minutes",
        "Persistence Minutes",
        "Cumulative Exceedance",
        "Peak Hour",
        "Average Heat",
        "Maximum Heat",
        "Shade Deficit",
        "Route Count",
        "Shelter Status",
        "Latitude",
        "Longitude",
    ]
    writer.writerow(headers)

    # Data rows
    stops = analysis.get("stops", [])
    for stop in stops:
        writer.writerow([
            stop.get("rank"),
            stop.get("id"),
            stop.get("name", ""),
            stop.get("priority_score"),
            stop.get("priority_category"),
            stop.get("heat_score"),
            stop.get("shade_score"),
            stop.get("vulnerability_score"),
            stop.get("transit_score"),
            stop.get("dangerous_minutes"),
            stop.get("persistence_minutes"),
            stop.get("cumulative_exceedance"),
            stop.get("peak_hour"),
            stop.get("average_heat"),
            stop.get("maximum_heat"),
            stop.get("shade_deficit"),
            stop.get("route_count"),
            stop.get("shelter_status"),
            stop.get("latitude"),
            stop.get("longitude"),
        ])

    # Footer
    writer.writerow([])
    writer.writerow(["# Methodology"])
    writer.writerow(["# Priority Score = 40% Heat + 25% Shade + 20% Vulnerability + 15% Transit"])
    writer.writerow(["# Heat Score = 50% Cumulative Exceedance + 30% Dangerous Minutes + 20% Persistence"])
    writer.writerow(["# All scores are percentile-normalized (0-100)"])
    writer.writerow([])
    writer.writerow(["# Assumptions"])
    writer.writerow(["# Shade deficit is a proxy from satellite land-cover data"])
    writer.writerow(["# Vulnerability uses Census tract-level community indicators"])
    writer.writerow(["# Transit importance uses route count as a proxy for ridership"])
    writer.writerow([])
    writer.writerow(["# Data Sources"])
    writer.writerow(["# FortyGuard heat analytics"])
    writer.writerow(["# Satellite land-cover segmentation"])
    writer.writerow(["# ACS 5-year 2022 Census estimates"])
    writer.writerow(["# CTtransit GTFS data"])

    return output.getvalue()


def get_report_metadata(analysis: dict) -> dict:
    """Extract report metadata from analysis result."""
    return {
        "analysis_id": analysis.get("analysis_id", ""),
        "city": analysis.get("city_id", "hartford-ct"),
        "analysis_date": analysis.get("start_time", "").split("T")[0],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_stops": analysis.get("total_stops", 0),
        "scoring_version": analysis.get("scoring_version", ""),
        "data_sources": [
            "FortyGuard heat analytics",
            "Satellite land-cover segmentation",
            "ACS 5-year 2022 Census estimates",
            "CTtransit GTFS data",
        ],
        "methodology": (
            "Priority Score = 40% Heat + 25% Shade + 20% Vulnerability + 15% Transit. "
            "Heat Score = 50% Cumulative Exceedance + 30% Dangerous Minutes + 20% Persistence. "
            "All component scores are percentile-normalized to 0-100."
        ),
        "assumptions": [
            "Analysis covers a single historical day",
            "Shade deficit is a proxy from satellite land-cover data",
            "Community vulnerability indicators use Census tract-level data",
            "Transit importance uses route count as a proxy for ridership",
        ],
        "limitations": [
            "Heat values are from one analysis period — seasonal variation is not captured",
            "Land-cover data does not directly measure shade at waiting position",
            "Census data is tract-level — individual variation exists",
            "Route count is a proxy — actual ridership may differ",
        ],
    }
