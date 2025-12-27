"""Caching utilities."""

import time
import json
import hashlib
import pickle
from typing import Any, Optional, Dict, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
from ..logging.logger import CoreLogger

logger = CoreLogger()


class CacheHelpers:
    """Simple in-memory caching utilities."""
    
    def __init__(self):
        """Initialize the cache."""
        self._cache: Dict[str, Any] = {}
        self._expiry: Dict[str, Optional[datetime]] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if key not found or expired
            
        Returns:
            Cached value or default
        """
        if key not in self._cache:
            self._stats['misses'] += 1
            return default
        
        # Check if expired
        expiry = self._expiry.get(key)
        if expiry and expiry <= datetime.now():
            # Remove expired item
            self.delete(key)
            self._stats['misses'] += 1
            return default
        
        self._stats['hits'] += 1
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
        """
        Set value in cache with optional TTL.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        self._cache[key] = value
        
        if ttl_seconds:
            expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            self._expiry[key] = expiry
        else:
            self._expiry[key] = None
        
        self._stats['sets'] += 1
        logger.log("cache", f"Set cache key: {key}", "debug")
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted
        """
        deleted = False
        if key in self._cache:
            del self._cache[key]
            deleted = True
        
        if key in self._expiry:
            del self._expiry[key]
            deleted = True
        
        if deleted:
            self._stats['deletes'] += 1
            logger.log("cache", f"Deleted cache key: {key}", "debug")
        
        return deleted
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._expiry.clear()
        logger.log("cache", "Cleared all cache entries", "info")
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries from cache.
        
        Returns:
            Number of expired entries removed
        """
        now = datetime.now()
        expired_keys = []
        
        for key, expiry in self._expiry.items():
            if expiry and expiry <= now:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.delete(key)
        
        if expired_keys:
            logger.log("cache", f"Cleaned up {len(expired_keys)} expired cache entries", "debug")
        
        return len(expired_keys)
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache and is not expired.
        
        Args:
            key: Cache key to check
            
        Returns:
            True if key exists and is not expired
        """
        if key not in self._cache:
            return False
        
        expiry = self._expiry.get(key)
        if expiry and expiry <= datetime.now():
            self.delete(key)
            return False
        
        return True
    
    def get_ttl(self, key: str) -> Optional[int]:
        """
        Get remaining time to live for a key.
        
        Args:
            key: Cache key
            
        Returns:
            Remaining TTL in seconds, None if no expiry or key doesn't exist
        """
        if not self.exists(key):
            return None
        
        expiry = self._expiry.get(key)
        if not expiry:
            return None
        
        remaining = (expiry - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def set_many(self, data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        """
        Set multiple key-value pairs.
        
        Args:
            data: Dictionary of key-value pairs
            ttl_seconds: Time to live for all entries
        """
        for key, value in data.items():
            self.set(key, value, ttl_seconds)
    
    def get_many(self, keys: list) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary of key-value pairs for found keys
        """
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def delete_many(self, keys: list) -> int:
        """
        Delete multiple keys from cache.
        
        Args:
            keys: List of cache keys to delete
            
        Returns:
            Number of keys deleted
        """
        deleted_count = 0
        for key in keys:
            if self.delete(key):
                deleted_count += 1
        return deleted_count
    
    def get_keys_by_pattern(self, pattern: str) -> list:
        """
        Get keys matching a pattern (simple wildcard support).
        
        Args:
            pattern: Pattern with * as wildcard
            
        Returns:
            List of matching keys
        """
        import fnmatch
        
        matching_keys = []
        for key in self._cache.keys():
            if fnmatch.fnmatch(key, pattern):
                matching_keys.append(key)
        
        return matching_keys
    
    def delete_by_pattern(self, pattern: str) -> int:
        """
        Delete keys matching a pattern.
        
        Args:
            pattern: Pattern with * as wildcard
            
        Returns:
            Number of keys deleted
        """
        keys_to_delete = self.get_keys_by_pattern(pattern)
        return self.delete_many(keys_to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        total_requests = self._stats['hits'] + self._stats['misses']
        hit_rate = (self._stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_keys': len(self._cache),
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'sets': self._stats['sets'],
            'deletes': self._stats['deletes'],
            'hit_rate_percent': round(hit_rate, 2),
            'total_requests': total_requests
        }
    
    def reset_stats(self) -> None:
        """Reset cache statistics."""
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }


class FileCache:
    """File-based cache implementation."""
    
    def __init__(self, cache_dir: str = 'cache'):
        """
        Initialize file cache.
        
        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = cache_dir
        from ..utils.file_ops import FileHelpers
        FileHelpers.ensure_directory(cache_dir)
    
    def _get_cache_path(self, key: str) -> str:
        """Get file path for cache key."""
        # Use hash of key to avoid filesystem issues
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return f"{self.cache_dir}/{key_hash}.cache"
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from file cache.
        
        Args:
            key: Cache key
            default: Default value if not found or expired
            
        Returns:
            Cached value or default
        """
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return default
        
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
            # Check if expired
            if data.get('expiry') and data['expiry'] <= datetime.now():
                self.delete(key)
                return default
            
            return data.get('value')
        except Exception as e:
            logger.log("cache", f"Error reading cache file {cache_path}: {e}", "error")
            return default
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
        """
        Set value in file cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if successful
        """
        cache_path = self._get_cache_path(key)
        
        try:
            expiry = None
            if ttl_seconds:
                expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            
            data = {
                'value': value,
                'expiry': expiry,
                'created': datetime.now()
            }
            
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            
            return True
        except Exception as e:
            logger.log("cache", f"Error writing cache file {cache_path}: {e}", "error")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from file cache.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if key was deleted
        """
        cache_path = self._get_cache_path(key)
        
        try:
            if os.path.exists(cache_path):
                os.remove(cache_path)
                return True
            return False
        except Exception as e:
            logger.log("cache", f"Error deleting cache file {cache_path}: {e}", "error")
            return False
    
    def clear(self) -> bool:
        """Clear all cache files."""
        try:
            import shutil
            if os.path.exists(self.cache_dir):
                shutil.rmtree(self.cache_dir)
                os.makedirs(self.cache_dir)
            return True
        except Exception as e:
            logger.log("cache", f"Error clearing cache directory: {e}", "error")
            return False


def cache_result(ttl_seconds: int = 300, key_func: Optional[Callable] = None, 
                cache_instance: Optional[CacheHelpers] = None):
    """
    Decorator to cache function results.
    
    Args:
        ttl_seconds: Time to live for cached results
        key_func: Function to generate cache key from arguments
        cache_instance: Cache instance to use (creates new one if None)
    
    Usage:
        @cache_result(ttl_seconds=60)
        def expensive_function(x, y):
            return x * y
    """
    if cache_instance is None:
        cache_instance = CacheHelpers()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


def cache_method(ttl_seconds: int = 300, key_prefix: str = ''):
    """
    Decorator to cache method results.
    
    Args:
        ttl_seconds: Time to live for cached results
        key_prefix: Prefix for cache key
    
    Usage:
        class MyClass:
            @cache_method(ttl_seconds=60, key_prefix='myclass')
            def expensive_method(self, x):
                return x * 2
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key including self identity
            self_id = id(self)
            key_data = f"{key_prefix}:{func.__name__}:{self_id}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Use instance cache if available, otherwise create one
            if not hasattr(self, '_method_cache'):
                self._method_cache = CacheHelpers()
            
            cache = self._method_cache
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute method and cache result
            result = func(self, *args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
cache = CacheHelpers()


def get_cache() -> CacheHelpers:
    """Get the global cache instance."""
    return cache


def cached(ttl_seconds: int = 300, key_func: Optional[Callable] = None):
    """
    Shortcut decorator using global cache.
    
    Args:
        ttl_seconds: Time to live for cached results
        key_func: Function to generate cache key from arguments
    """
    return cache_result(ttl_seconds, key_func, cache)
