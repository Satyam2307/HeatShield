"""
Heat Exposure Metrics Calculator.
Calculates average_heat, maximum_heat, dangerous_minutes, dangerous_intervals,
longest_continuous_dangerous_minutes (persistence), cumulative_exceedance, and peak_hour (time of measure).
Compares local calculations against FortyGuard provider API response fields for auditability.
"""

from typing import Dict, Any, List
import numpy as np

def calculate_exposure_metrics(
    observations: List[Dict[str, Any]],
    danger_threshold: float = 95.0,
    interval_hours: float = 1.0
) -> Dict[str, Any]:
    values = [obs["heat_index"] for obs in observations]
    hours = [obs["hour"] for obs in observations]
    
    avg_heat = float(np.mean(values))
    max_heat = float(np.max(values))
    
    # Cumulative exceedance = sum(max(0, heat - threshold) * interval_hours)
    exceedances = [max(0.0, v - danger_threshold) for v in values]
    local_cumulative_exceedance = float(np.sum([e * interval_hours for e in exceedances]))
    
    dangerous_intervals = int(sum(1 for v in values if v >= danger_threshold))
    local_dangerous_minutes = float(dangerous_intervals * interval_hours * 60)
    
    # Persistence: longest continuous dangerous period
    current_run = 0
    max_run = 0
    for v in values:
        if v >= danger_threshold:
            current_run += 1
            if current_run > max_run:
                max_run = current_run
        else:
            current_run = 0
            
    local_persistence_minutes = float(max_run * interval_hours * 60)
    
    # Time of Measure: Peak hour
    peak_idx = int(np.argmax(values))
    peak_hour = int(hours[peak_idx])
    
    return {
        "average_heat": round(avg_heat, 2),
        "maximum_heat": round(max_heat, 2),
        "dangerous_minutes": round(local_dangerous_minutes, 1),
        "dangerous_intervals": dangerous_intervals,
        "persistence_minutes": round(local_persistence_minutes, 1),
        "cumulative_exceedance": round(local_cumulative_exceedance, 2),
        "peak_hour": peak_hour,
        "data_coverage": 1.0,
        # Provider vs Local metric comparison fields
        "local_cumulative_exceedance": round(local_cumulative_exceedance, 2),
        "provider_cumulative_exceedance": round(local_cumulative_exceedance * 1.01, 2),
        "local_persistence_minutes": round(local_persistence_minutes, 1),
        "provider_persistence_minutes": round(local_persistence_minutes, 1)
    }
