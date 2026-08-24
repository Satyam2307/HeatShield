"""
File-system cache for API responses and computed results.

Used instead of Redis for hackathon simplicity.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path

from app.config import CACHE_DIR


class FileCache:
    """Simple filesystem-based cache with TTL support."""

    def __init__(self, cache_dir: str | Path | None = None, default_ttl: int = 86400):
        self.cache_dir = Path(cache_dir or CACHE_DIR)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.default_ttl = default_ttl

    def _make_key(self, provider: str, endpoint: str, **params) -> str:
        """Create a deterministic cache key from request parameters."""
        key_data = {
            "provider": provider,
            "endpoint": endpoint,
            **{k: str(v) for k, v in sorted(params.items())},
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()

    def _cache_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.json"

    def _meta_path(self, key: str) -> Path:
        return self.cache_dir / f"{key}.meta.json"

    def get(self, provider: str, endpoint: str, **params) -> dict | None:
        """Retrieve a cached response, or None if expired/missing."""
        key = self._make_key(provider, endpoint, **params)
        cache_file = self._cache_path(key)
        meta_file = self._meta_path(key)

        if not cache_file.exists():
            return None

        # Check TTL
        if meta_file.exists():
            meta = json.loads(meta_file.read_text())
            if time.time() > meta.get("expires_at", 0):
                cache_file.unlink(missing_ok=True)
                meta_file.unlink(missing_ok=True)
                return None

        try:
            return json.loads(cache_file.read_text())
        except (json.JSONDecodeError, OSError):
            return None

    def set(
        self,
        data: dict,
        provider: str,
        endpoint: str,
        ttl: int | None = None,
        **params,
    ) -> None:
        """Store a response in the cache."""
        key = self._make_key(provider, endpoint, **params)
        cache_file = self._cache_path(key)
        meta_file = self._meta_path(key)

        cache_file.write_text(json.dumps(data))
        meta = {
            "provider": provider,
            "endpoint": endpoint,
            "params": params,
            "cached_at": time.time(),
            "expires_at": time.time() + (ttl or self.default_ttl),
        }
        meta_file.write_text(json.dumps(meta))

    def clear(self) -> int:
        """Clear all cached files. Returns count of removed files."""
        count = 0
        for f in self.cache_dir.glob("*.json"):
            f.unlink()
            count += 1
        return count


# Singleton
cache = FileCache()
