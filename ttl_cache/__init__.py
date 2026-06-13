"""ttl-cache — a tiny thread-safe cache with per-entry TTL and optional max size.

Entries expire after their time-to-live; an optional capacity evicts the oldest
(insertion-order / LRU-on-access) entry when full. Lazy expiry on read plus an
explicit purge(). No background threads, no dependencies.

Zero dependencies. Pure standard library. MIT licensed. Original implementation.
"""
from __future__ import annotations
import time
import threading
from collections import OrderedDict
from typing import Any, Callable, Optional

__version__ = "0.1.0"
__all__ = ["TTLCache"]

_MISSING = object()


class TTLCache:
    def __init__(self, default_ttl: float = 60.0, max_size: Optional[int] = None,
                 time_fn: Callable[[], float] = time.monotonic) -> None:
        if default_ttl <= 0:
            raise ValueError("default_ttl must be > 0")
        if max_size is not None and max_size < 1:
            raise ValueError("max_size must be >= 1")
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._now = time_fn
        self._data: "OrderedDict[Any, tuple]" = OrderedDict()  # key -> (value, expires_at)
        self._lock = threading.Lock()
        self.hits = 0
        self.misses = 0

    def _expired(self, expires_at: float) -> bool:
        return self._now() >= expires_at

    def set(self, key: Any, value: Any, ttl: Optional[float] = None) -> None:
        ttl = self.default_ttl if ttl is None else ttl
        if ttl <= 0:
            raise ValueError("ttl must be > 0")
        with self._lock:
            if key in self._data:
                self._data.move_to_end(key)
            self._data[key] = (value, self._now() + ttl)
            if self.max_size is not None:
                while len(self._data) > self.max_size:
                    self._data.popitem(last=False)   # evict oldest

    def get(self, key: Any, default: Any = None) -> Any:
        with self._lock:
            item = self._data.get(key, _MISSING)
            if item is _MISSING:
                self.misses += 1
                return default
            value, expires_at = item
            if self._expired(expires_at):
                del self._data[key]
                self.misses += 1
                return default
            self._data.move_to_end(key)   # LRU on access
            self.hits += 1
            return value

    def get_or_set(self, key: Any, factory: Callable[[], Any], ttl: Optional[float] = None) -> Any:
        val = self.get(key, _MISSING)
        if val is _MISSING:
            val = factory()
            self.set(key, val, ttl)
        return val

    def delete(self, key: Any) -> bool:
        with self._lock:
            return self._data.pop(key, _MISSING) is not _MISSING

    def purge(self) -> int:
        """Remove all expired entries; return count removed."""
        with self._lock:
            dead = [k for k, (_, exp) in self._data.items() if self._expired(exp)]
            for k in dead:
                del self._data[k]
            return len(dead)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()

    def __len__(self) -> int:
        self.purge()
        with self._lock:
            return len(self._data)

    def __contains__(self, key: Any) -> bool:
        return self.get(key, _MISSING) is not _MISSING
