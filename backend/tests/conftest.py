"""Pytest fixtures for HeatShield backend tests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# Ensure backend is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def sample_values():
    """Sample heat values for testing (hourly 10AM-6PM)."""
    return [92.0, 94.5, 96.8, 99.1, 101.3, 100.2, 98.7, 95.4, 93.1]


@pytest.fixture
def sample_timestamps():
    """Corresponding timestamps for sample values."""
    return [
        "2023-07-27T10:00:00-04:00",
        "2023-07-27T11:00:00-04:00",
        "2023-07-27T12:00:00-04:00",
        "2023-07-27T13:00:00-04:00",
        "2023-07-27T14:00:00-04:00",
        "2023-07-27T15:00:00-04:00",
        "2023-07-27T16:00:00-04:00",
        "2023-07-27T17:00:00-04:00",
        "2023-07-27T18:00:00-04:00",
    ]


@pytest.fixture
def threshold():
    """Default danger threshold (°F)."""
    return 95.0


@pytest.fixture
def analysis_result():
    """Load a pre-computed analysis result for API tests."""
    from app.services.analysis_service import run_analysis
    return run_analysis(analysis_id="test-001")
