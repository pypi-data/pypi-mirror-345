"""
Utility functions for working with the address cache.
"""
import hashlib
import json
from typing import Dict, Any, Optional

from .cache_manager import CacheManager

# Global cache manager instance
_cache_manager = None


def get_cache_manager() -> CacheManager:
    """
    Get the global cache manager instance.
    
    Returns:
        CacheManager: The global cache manager instance.
    """
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager


def generate_cache_key(address_data: Dict[str, Any]) -> str:
    """
    Generate a cache key for the given address data.
    
    Args:
        address_data: The address data to generate a key for.
        
    Returns:
        str: A cache key.
    """
    # Sort the dictionary to ensure consistent key generation
    sorted_data = json.dumps(address_data, sort_keys=True)
    return hashlib.md5(sorted_data.encode('utf-8')).hexdigest()


def get_cached_address(address_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Get a cached formatted address if available.
    
    Args:
        address_data: The address data to look up.
        
    Returns:
        Dict[str, Any] or None: The cached formatted address if available, otherwise None.
    """
    cache_key = generate_cache_key(address_data)
    cache_manager = get_cache_manager()
    return cache_manager.get(cache_key)


def cache_formatted_address(address_data: Dict[str, Any], formatted_result: Dict[str, Any]) -> None:
    """
    Cache a formatted address result.
    
    Args:
        address_data: The input address data.
        formatted_result: The formatted address result.
    """
    cache_key = generate_cache_key(address_data)
    cache_manager = get_cache_manager()
    cache_manager.set(cache_key, formatted_result)


def clear_cache() -> None:
    """
    Clear all cached addresses.
    """
    cache_manager = get_cache_manager()
    cache_manager.clear() 