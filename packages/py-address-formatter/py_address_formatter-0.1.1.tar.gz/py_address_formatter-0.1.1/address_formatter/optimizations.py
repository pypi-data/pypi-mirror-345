"""
Performance optimizations for the address formatter.

This module provides optimization utilities for improving memory usage
and computational performance of the address formatter.
"""

import re
import time
from functools import lru_cache, wraps
from typing import Dict, Any, Callable, TypeVar, List, Set, Optional, Union, Pattern

T = TypeVar('T')

# Memory optimization

def memoize(func: Callable[..., T]) -> Callable[..., T]:
    """
    Memoize a function result based on its arguments.
    
    This is more flexible than lru_cache as it supports unhashable arguments
    by using a custom key function.
    
    Args:
        func: Function to memoize.
        
    Returns:
        Memoized function.
    """
    cache: Dict[str, T] = {}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create a cache key based on args and kwargs
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key = ":".join(key_parts)
        
        # Check cache
        if key in cache:
            return cache[key]
        
        # Compute result and cache it
        result = func(*args, **kwargs)
        cache[key] = result
        return result
    
    # Add cache clear method
    def clear_cache() -> None:
        """Clear the memoization cache."""
        cache.clear()
    
    wrapper.clear_cache = clear_cache  # type: ignore
    
    return wrapper

def object_pool(cls):
    """
    Class decorator to implement object pooling.
    
    This reduces the overhead of object creation by reusing 
    instances of immutable objects.
    
    Args:
        cls: Class to pool.
        
    Returns:
        Pooled class.
    """
    pool: Dict[str, Any] = {}
    
    # Save original __new__ method
    original_new = cls.__new__
    
    def pooled_new(cls, *args, **kwargs):
        # Create a cache key based on args and kwargs
        key_parts = [str(arg) for arg in args]
        key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
        key = ":".join(key_parts)
        
        # Check pool
        if key in pool:
            return pool[key]
        
        # Create new instance
        instance = original_new(cls, *args, **kwargs)
        
        # Add to pool
        pool[key] = instance
        
        return instance
    
    # Replace __new__ method
    cls.__new__ = pooled_new  # type: ignore
    
    return cls

class StringIntern:
    """
    String interning utility to reduce memory usage.
    
    This utility interns strings to avoid duplicate string objects,
    reducing memory usage when dealing with many repeated strings.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._strings: Dict[str, str] = {}
        return cls._instance
    
    def intern(self, s: str) -> str:
        """
        Intern a string.
        
        Args:
            s: String to intern.
            
        Returns:
            Interned string.
        """
        if s in self._strings:
            return self._strings[s]
        
        self._strings[s] = s
        return s
    
    def clear(self) -> None:
        """Clear the interned strings."""
        self._strings.clear()

# Computational optimization

class RegexCache:
    """
    Regex pattern cache to avoid recompiling regular expressions.
    
    This utility caches compiled regex patterns to avoid the overhead
    of recompiling them for each use.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._patterns: Dict[str, Pattern] = {}
        return cls._instance
    
    def get(self, pattern: str, flags: int = 0) -> Pattern:
        """
        Get a compiled regex pattern.
        
        Args:
            pattern: Regex pattern string.
            flags: Regex flags.
            
        Returns:
            Compiled regex pattern.
        """
        key = f"{pattern}:{flags}"
        
        if key not in self._patterns:
            self._patterns[key] = re.compile(pattern, flags)
        
        return self._patterns[key]
    
    def clear(self) -> None:
        """Clear the pattern cache."""
        self._patterns.clear()

@lru_cache(maxsize=1000)
def compile_pattern(pattern: str, flags: int = 0) -> Pattern:
    """
    Compile a regex pattern with caching.
    
    Args:
        pattern: Regex pattern string.
        flags: Regex flags.
        
    Returns:
        Compiled regex pattern.
    """
    return re.compile(pattern, flags)

def optimize_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimize a dictionary by interning string keys and values.
    
    Args:
        d: Dictionary to optimize.
        
    Returns:
        Optimized dictionary.
    """
    intern = StringIntern()
    result = {}
    
    for k, v in d.items():
        if isinstance(k, str):
            k = intern.intern(k)
        
        if isinstance(v, str):
            v = intern.intern(v)
        elif isinstance(v, dict):
            v = optimize_dict(v)
        
        result[k] = v
    
    return result

try:
    # Attempt to import optional numba if available
    import numba
    
    @numba.jit(nopython=True)
    def _optimize_template_match(template: str, components: Dict[str, str]) -> str:
        """
        Optimized template matching with JIT compilation.
        
        Args:
            template: Template string.
            components: Address components.
            
        Returns:
            Rendered string.
        """
        # This is a placeholder for the actual implementation
        # The real implementation would depend on how templates are structured
        return ""
    
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False

def use_jit(func: Callable[..., T]) -> Callable[..., T]:
    """
    Decorator to use JIT compilation if available.
    
    Args:
        func: Function to optimize.
        
    Returns:
        Optimized function (JIT-compiled if numba is available).
    """
    if HAS_NUMBA:
        try:
            return numba.jit(nopython=True)(func)
        except:
            # Fall back to original function if JIT compilation fails
            return func
    return func

class Timer:
    """
    Simple timer for performance profiling.
    
    This utility measures the execution time of code blocks.
    """
    
    def __init__(self, name: str = ""):
        """
        Initialize a timer.
        
        Args:
            name: Timer name for identification.
        """
        self.name = name
        self.start_time = 0.0
        self.elapsed = 0.0
    
    def __enter__(self):
        """Start timing on context entry."""
        self.start_time = time.time()
        return self
    
    def __exit__(self, *args):
        """Stop timing on context exit."""
        self.elapsed = time.time() - self.start_time
        if self.name:
            print(f"{self.name}: {self.elapsed:.6f} seconds")
    
    def reset(self):
        """Reset the timer."""
        self.start_time = time.time()
        self.elapsed = 0.0 