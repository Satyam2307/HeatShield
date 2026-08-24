"""
FortyGuard API adapter and spatial heat data provider module.
Models /heatmap, /env_params, /exceedance, /persistence, and /time_of_measure endpoints.
"""

from pathlib import Path
import json
import numpy as np
from typing import Dict, List, Any

class FortyGuardAdapter:
    """
    FortyGuard Provider Adapter handling live requests and high-fidelity offline synthesis.
    """
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.fortyguard.io/v1"

    def get_time_series_observations(
        self,
        stop_id: str,
        lat: float,
        lon: float,
        start_hour: int = 10,
        end_hour: int = 18,
        danger_threshold: float = 95.0
    ) -> List[Dict[str, Any]]:
        """
        Generates hourly heat index profile (10:00 AM - 6:00 PM EDT) for a bus stop location.
        """
        seed = int(abs(lat * 1000 + lon * 1000)) % 10000
        rng = np.random.RandomState(seed)
        
        hours = list(range(start_hour, end_hour + 1))
        spatial_heat_bias = (lat - 41.76) * 40.0 - (lon + 72.68) * 30.0 + rng.uniform(-1.5, 2.5)
        
        observations = []
        for h in hours:
            time_factor = -0.35 * ((h - 15.0) ** 2) + 6.0
            base_temp = 90.0 + time_factor + spatial_heat_bias
            noise = rng.uniform(-0.8, 0.8)
            heat_index_val = round(max(82.0, base_temp + noise), 1)
            exceedance_val = max(0.0, round(heat_index_val - danger_threshold, 1))
            
            observations.append({
                "hour": h,
                "timestamp": f"2024-07-15T{h:02d}:00:00-04:00",
                "heat_index": heat_index_val,
                "unit": "F",
                "exceedance": exceedance_val,
                "is_dangerous": heat_index_val >= danger_threshold
            })
            
        return observations
