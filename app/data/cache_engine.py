"""
Antigravity — Safe Cache Engine

Wraps data retrieval to improve performance without altering core pipeline logic.
Provides TTL-based caching for API responses and dashboard aggregations.

Cache Location: cache/api/, cache/dashboard/
"""

import json
import os
from datetime import datetime, timezone
from typing import Callable, Any, Optional

CACHE_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "cache"
)

API_CACHE_DIR = os.path.join(CACHE_DIR, "api")
DASHBOARD_CACHE_DIR = os.path.join(CACHE_DIR, "dashboard")


def _get_cache_path(key: str, cache_type: str) -> str:
    target_dir = DASHBOARD_CACHE_DIR if cache_type == "dashboard" else API_CACHE_DIR
    os.makedirs(target_dir, exist_ok=True)
    return os.path.join(target_dir, f"{key}.json")


def load_cache(key: str, cache_type: str = "api", ttl_seconds: int = 3600) -> Optional[Any]:
    """Attempt to load data from cache if it is within TTL."""
    path = _get_cache_path(key, cache_type)
    
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        timestamp = data.get("timestamp", 0)
        current_time = datetime.now(timezone.utc).timestamp()
        
        if current_time - timestamp <= ttl_seconds:
            print(f"    [Cache Hit] Loaded {key} from {cache_type} cache")
            return data.get("payload")
        else:
            print(f"    [Cache Expired] Refreshing {key} data")
            return None
            
    except Exception as e:
        print(f"    [WARN] Cache read failed for {key}: {e}")
        return None


def save_cache(key: str, payload: Any, cache_type: str = "api") -> None:
    """Save data payload to cache with a timestamp."""
    path = _get_cache_path(key, cache_type)
    
    data = {
        "timestamp": datetime.now(timezone.utc).timestamp(),
        "payload": payload
    }
    
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"    [WARN] Cache write failed for {key}: {e}")


def cached_fetch(
    key: str, 
    fetch_function: Callable[[], Any], 
    cache_type: str = "api", 
    ttl_seconds: int = 3600
) -> Any:
    """
    Wrapper to automatically check cache before calling fetch_function.
    If cache misses or is expired, fetch_function is called and result is cached.
    """
    cached_data = load_cache(key, cache_type, ttl_seconds)
    if cached_data is not None:
        return cached_data

    # Cache miss or expired, fetch real data
    data = fetch_function()
    
    # Only cache if data was successfully successfully retrieved
    if data is not None:
        save_cache(key, data, cache_type)
        
    return data
