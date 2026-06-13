# ttl-cache

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Zero dependencies](https://img.shields.io/badge/dependencies-0-brightgreen.svg)](#)

A tiny **thread-safe cache with per-entry TTL** and optional max size. Entries expire
after their time-to-live; an optional capacity evicts the least-recently-used entry.
Lazy expiry on read, explicit `purge()`, no background threads. Zero dependencies.

## Install
```bash
pip install ttl-cache-wcn
```

## Use
```python
from ttl_cache import TTLCache

cache = TTLCache(default_ttl=60, max_size=10_000)
cache.set("k", "v")              # expires in 60s
cache.set("hot", x, ttl=5)       # per-entry TTL
cache.get("k")                   # "v" (or None once expired)

cache.get_or_set("user:42", lambda: load_user(42))   # compute-once-on-miss
```

## Features
- ✅ Per-entry TTL (lazy expiry on read)
- ✅ Optional `max_size` with LRU-on-access eviction
- ✅ `get_or_set`, `purge`, `delete`, `clear`, `in`, `len`
- ✅ Injectable clock (deterministic tests)
- ✅ Hit/miss counters
- ✅ **Zero dependencies**

## License
MIT © WCN Development Co
