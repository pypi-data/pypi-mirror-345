"""
Cache manager for the address formatter.
"""
import os
import json
import time
from typing import Dict, Any, Optional


class CacheManager:
    """
    Manages caching for formatted addresses to improve performance.
    """
    
    def __init__(self, cache_dir: Optional[str] = None, max_age: int = 86400):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory to store cache files. If None, uses the default directory.
            max_age: Maximum age of cache entries in seconds. Default is 24 hours.
        """
        if cache_dir is None:
            # Use the default cache directory within the package
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.cache_dir = os.path.join(base_dir, "data")
        else:
            self.cache_dir = cache_dir
            
        # Create cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        self.max_age = max_age
        self.cache: Dict[str, Any] = {}
        self.loaded = False
    
    def _get_cache_file_path(self) -> str:
        """
        Get the path to the cache file.
        
        Returns:
            str: Path to the cache file.
        """
        return os.path.join(self.cache_dir, "address_cache.json")
    
    def _load_cache(self) -> None:
        """
        Load cache from disk.
        """
        cache_file = self._get_cache_file_path()
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    self.cache = data
            except (json.JSONDecodeError, IOError):
                # If cache file is corrupted or can't be read, start with empty cache
                self.cache = {}
        self.loaded = True
    
    def _save_cache(self) -> None:
        """
        Save cache to disk.
        """
        cache_file = self._get_cache_file_path()
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.cache, f)
        except IOError:
            # If we can't write the cache, just continue without caching
            pass
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get a value from the cache.
        
        Args:
            key: Cache key to look up.
            
        Returns:
            The cached value or None if not found or expired.
        """
        if not self.loaded:
            self._load_cache()
        
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        timestamp = entry.get("timestamp", 0)
        
        # Check if entry has expired
        if time.time() - timestamp > self.max_age:
            # Remove expired entry
            del self.cache[key]
            self._save_cache()
            return None
            
        return entry.get("data")
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key.
            value: Value to cache.
        """
        if not self.loaded:
            self._load_cache()
        
        self.cache[key] = {
            "timestamp": time.time(),
            "data": value
        }
        self._save_cache()
    
    def clear(self) -> None:
        """
        Clear all cache entries.
        """
        self.cache = {}
        self._save_cache()
        
    def remove(self, key: str) -> None:
        """
        Remove a specific entry from the cache.
        
        Args:
            key: Cache key to remove.
        """
        if not self.loaded:
            self._load_cache()
            
        if key in self.cache:
            del self.cache[key]
            self._save_cache() 