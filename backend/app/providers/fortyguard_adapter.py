"""
FortyGuard API adapter.

Isolated provider interface for all FortyGuard API interactions.
Handles authentication, timeouts, retries, caching, and response normalization.

IMPORTANT: Do not invent endpoint paths or payloads.
This adapter is structured based on documented FortyGuard capabilities.
Update method implementations when official documentation is confirmed.
"""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any

import httpx

from app.cache.file_cache import cache
from app.config import settings

logger = logging.getLogger(__name__)


class FortyGuardError(Exception):
    """FortyGuard API error."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class FortyGuardAdapter:
    """
    Adapter for FortyGuard heat analytics API.

    All methods follow the pattern:
        1. Check cache
        2. Build request (auth, headers, body)
        3. Send with timeout + retry
        4. Validate response
        5. Cache successful response
        6. Normalize to internal models
        7. Return or raise
    """

    def __init__(self):
        self.base_url = settings.fortyguard_base_url.rstrip("/") if settings.fortyguard_base_url else ""
        self.api_key = settings.fortyguard_api_key
        self.timeout = settings.fortyguard_timeout_seconds
        self.max_retries = settings.fortyguard_max_retries

    @property
    def is_configured(self) -> bool:
        """Check if FortyGuard credentials are available."""
        return bool(self.base_url and self.api_key)

    def _headers(self) -> dict[str, str]:
        """Build request headers with authentication."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _cache_key(self, endpoint: str, **params) -> dict:
        """Build cache key parameters."""
        return {"provider": "fortyguard", "endpoint": endpoint, **params}

    async def _request(
        self,
        method: str,
        path: str,
        body: dict | None = None,
        cache_key_params: dict | None = None,
    ) -> dict:
        """
        Make an authenticated request to FortyGuard.

        Args:
            method: HTTP method ('GET' or 'POST').
            path: API path (e.g., '/v1/env_params').
            body: Request body for POST requests.
            cache_key_params: Additional cache key parameters.

        Returns:
            Parsed JSON response.

        Raises:
            FortyGuardError: On API errors.
        """
        if not self.is_configured:
            raise FortyGuardError("FortyGuard API is not configured", status_code=None)

        # Check cache
        if cache_key_params:
            cached = cache.get(**self._cache_key(path, **cache_key_params))
            if cached:
                logger.info("FortyGuard cache hit for %s", path)
                return cached

        url = f"{self.base_url}{path}"

        # Log request metadata (never the API key)
        logger.info(
            "FortyGuard request: %s %s (timeout=%ds)",
            method, path, self.timeout,
        )

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method.upper() == "POST":
                        response = await client.post(url, json=body, headers=self._headers())
                    else:
                        response = await client.get(url, headers=self._headers())

                if response.status_code == 200:
                    data = response.json()
                    # Cache successful response
                    if cache_key_params:
                        cache.set(data, **self._cache_key(path, **cache_key_params))
                    return data

                if response.status_code >= 500 and attempt < self.max_retries:
                    logger.warning(
                        "FortyGuard %s returned %d, retrying (%d/%d)",
                        path, response.status_code, attempt + 1, self.max_retries,
                    )
                    continue

                raise FortyGuardError(
                    f"FortyGuard {path} returned {response.status_code}: {response.text}",
                    status_code=response.status_code,
                )

            except httpx.TimeoutException as e:
                last_error = e
                if attempt < self.max_retries:
                    logger.warning("FortyGuard timeout for %s, retrying", path)
                    continue
            except httpx.HTTPError as e:
                last_error = e
                if attempt < self.max_retries:
                    continue

        raise FortyGuardError(f"FortyGuard request failed after {self.max_retries + 1} attempts: {last_error}")

    # -----------------------------------------------------------------
    # Public API methods — structured per FortyGuard documentation
    # -----------------------------------------------------------------

    async def get_heatmap(
        self,
        polygon: list[list[float]],
        start_time: str,
        end_time: str,
        analytic_type: str = "heat_index",
    ) -> dict:
        """
        Get heatmap data for a polygon and time range.

        Returns normalized heat grid data.
        """
        body = {
            "polygon": polygon,
            "start_time": start_time,
            "end_time": end_time,
            "analytic_type": analytic_type,
        }
        key_hash = hashlib.md5(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]
        return await self._request(
            "POST", "/v1/heatmap",
            body=body,
            cache_key_params={"hash": key_hash},
        )

    async def get_environment_parameters(
        self,
        polygon: list[list[float]],
        start_time: str,
        end_time: str,
    ) -> dict:
        """
        Get environmental parameters (temperature, humidity, wind, etc.).

        Uses POST /v1/env_params as documented.
        """
        body = {
            "polygon": polygon,
            "start_time": start_time,
            "end_time": end_time,
        }
        key_hash = hashlib.md5(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]
        return await self._request(
            "POST", "/v1/env_params",
            body=body,
            cache_key_params={"hash": key_hash},
        )

    async def get_satellite_landcover(
        self,
        polygon: list[list[float]],
    ) -> dict:
        """
        Get satellite/land-cover segmentation data.

        Uses POST /v1/satellite as documented.
        """
        body = {"polygon": polygon}
        key_hash = hashlib.md5(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]
        return await self._request(
            "POST", "/v1/satellite",
            body=body,
            cache_key_params={"hash": key_hash},
        )

    async def get_exceedance(
        self,
        polygon: list[list[float]],
        start_time: str,
        end_time: str,
        threshold: float,
        metric: str = "heat_index",
    ) -> dict:
        """Get exceedance data — how much and how long above threshold."""
        body = {
            "polygon": polygon,
            "start_time": start_time,
            "end_time": end_time,
            "threshold": threshold,
            "analytic_type": "exceedance",
            "metric": metric,
        }
        key_hash = hashlib.md5(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]
        return await self._request(
            "POST", "/v1/heatmap",
            body=body,
            cache_key_params={"hash": key_hash},
        )

    async def get_persistence(
        self,
        polygon: list[list[float]],
        start_time: str,
        end_time: str,
        threshold: float,
        metric: str = "heat_index",
    ) -> dict:
        """Get persistence data — duration of continuous exceedance."""
        body = {
            "polygon": polygon,
            "start_time": start_time,
            "end_time": end_time,
            "threshold": threshold,
            "analytic_type": "persistence",
            "metric": metric,
        }
        key_hash = hashlib.md5(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]
        return await self._request(
            "POST", "/v1/heatmap",
            body=body,
            cache_key_params={"hash": key_hash},
        )

    async def get_time_of_measure(
        self,
        polygon: list[list[float]],
        start_time: str,
        end_time: str,
        filter_type: int = 3,  # Entire day
    ) -> dict:
        """
        Get time-of-measure data — when peak heat occurs.

        Uses analytic_type=time_of_measure and filter_type=3 for full day.
        """
        body = {
            "polygon": polygon,
            "start_time": start_time,
            "end_time": end_time,
            "analytic_type": "time_of_measure",
            "filter_type": filter_type,
        }
        key_hash = hashlib.md5(json.dumps(body, sort_keys=True).encode()).hexdigest()[:12]
        return await self._request(
            "POST", "/v1/heatmap",
            body=body,
            cache_key_params={"hash": key_hash},
        )


# Singleton
fortyguard = FortyGuardAdapter()
