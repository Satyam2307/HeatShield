"""Tests for geospatial utilities."""

import json
from pathlib import Path

from app.geospatial.boundary import load_hartford_boundary, get_hartford_bbox, point_in_hartford
from app.geospatial.buffers import create_buffer_wgs84


def test_load_hartford_boundary():
    boundary = load_hartford_boundary()
    assert boundary["type"] == "FeatureCollection"
    assert len(boundary["features"]) > 0
    assert boundary["features"][0]["properties"]["name"] == "Hartford"


def test_hartford_bbox():
    bbox = get_hartford_bbox()
    assert len(bbox) == 4
    # Hartford is roughly at -72.7 lon, 41.76 lat
    assert -73 < bbox[0] < -72
    assert 41 < bbox[1] < 42


def test_point_in_hartford_center():
    # Hartford city center should be inside
    assert point_in_hartford(-72.6851, 41.7637) is True


def test_point_outside_hartford():
    # New York City should not be in Hartford
    assert point_in_hartford(-74.006, 40.7128) is False


def test_buffer_creation():
    buffer = create_buffer_wgs84(-72.6851, 41.7637, 100)
    assert buffer["type"] == "Polygon"
    assert len(buffer["coordinates"][0]) > 10  # Should have many points in circle


def test_buffer_clamping():
    # Should not exceed max buffer
    buffer_big = create_buffer_wgs84(-72.6851, 41.7637, 1000)  # Exceeds 500m max
    buffer_max = create_buffer_wgs84(-72.6851, 41.7637, 500)
    # Both should produce same-size buffer due to clamping
    assert len(buffer_big["coordinates"][0]) == len(buffer_max["coordinates"][0])
