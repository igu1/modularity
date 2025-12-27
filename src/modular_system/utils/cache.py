                        

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
                                             
    
    def __init__(self):
                                   
        self._cache: Dict[str, Any] = {}
        self._expiry: Dict[str, Optional[datetime]] = {}
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }
    
    def get(self, key: str, default: Any = None) -> Any:
\
\
\
\
\
\
\
\
\
           
        if key not in self._cache:
            self._stats['misses'] += 1
            return default
        
                          
        expiry = self._expiry.get(key)
        if expiry and expiry <= datetime.now():
                                 
            self.delete(key)
            self._stats['misses'] += 1
            return default
        
        self._stats['hits'] += 1
        return self._cache[key]
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
\
\
\
\
\
\
\
           
        self._cache[key] = value
        
        if ttl_seconds:
            expiry = datetime.now() + timedelta(seconds=ttl_seconds)
            self._expiry[key] = expiry
        else:
            self._expiry[key] = None
        
        self._stats['sets'] += 1
        logger.log("cache", f"Set cache key: {key}", "debug")
    
    def delete(self, key: str) -> bool:
\
\
\
\
\
\
\
\
           
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
                                      
        self._cache.clear()
        self._expiry.clear()
        logger.log("cache", "Cleared all cache entries", "info")
    
    def cleanup_expired(self) -> int:
\
\
\
\
\
           
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
\
\
\
\
\
\
\
\
           
        if key not in self._cache:
            return False
        
        expiry = self._expiry.get(key)
        if expiry and expiry <= datetime.now():
            self.delete(key)
            return False
        
        return True
    
    def get_ttl(self, key: str) -> Optional[int]:
\
\
\
\
\
\
\
\
           
        if not self.exists(key):
            return None
        
        expiry = self._expiry.get(key)
        if not expiry:
            return None
        
        remaining = (expiry - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def set_many(self, data: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
\
\
\
\
\
\
           
        for key, value in data.items():
            self.set(key, value, ttl_seconds)
    
    def get_many(self, keys: list) -> Dict[str, Any]:
\
\
\
\
\
\
\
\
           
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result
    
    def delete_many(self, keys: list) -> int:
\
\
\
\
\
\
\
\
           
        deleted_count = 0
        for key in keys:
            if self.delete(key):
                deleted_count += 1
        return deleted_count
    
    def get_keys_by_pattern(self, pattern: str) -> list:
\
\
\
\
\
\
\
\
           
        import fnmatch
        
        matching_keys = []
        for key in self._cache.keys():
            if fnmatch.fnmatch(key, pattern):
                matching_keys.append(key)
        
        return matching_keys
    
    def delete_by_pattern(self, pattern: str) -> int:
\
\
\
\
\
\
\
\
           
        keys_to_delete = self.get_keys_by_pattern(pattern)
        return self.delete_many(keys_to_delete)
    
    def get_stats(self) -> Dict[str, Any]:
\
\
\
\
\
           
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
                                     
        self._stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0
        }


class FileCache:
                                          
    
    def __init__(self, cache_dir: str = 'cache'):
\
\
\
\
\
           
        self.cache_dir = cache_dir
        from ..utils.file_ops import FileHelpers
        FileHelpers.ensure_directory(cache_dir)
    
    def _get_cache_path(self, key: str) -> str:
                                          
                                                    
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return f"{self.cache_dir}/{key_hash}.cache"
    
    def get(self, key: str, default: Any = None) -> Any:
\
\
\
\
\
\
\
\
\
           
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return default
        
        try:
            with open(cache_path, 'rb') as f:
                data = pickle.load(f)
            
                              
            if data.get('expiry') and data['expiry'] <= datetime.now():
                self.delete(key)
                return default
            
            return data.get('value')
        except Exception as e:
            logger.log("cache", f"Error reading cache file {cache_path}: {e}", "error")
            return default
    
    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None) -> bool:
\
\
\
\
\
\
\
\
\
\
           
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
\
\
\
\
\
\
\
\
           
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
\
\
\
\
\
\
\
\
\
\
\
\
       
    if cache_instance is None:
        cache_instance = CacheHelpers()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
                                
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                                        
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
                                   
            cached_result = cache_instance.get(cache_key)
            if cached_result is not None:
                return cached_result
            
                                               
            result = func(*args, **kwargs)
            cache_instance.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


def cache_method(ttl_seconds: int = 300, key_prefix: str = ''):
\
\
\
\
\
\
\
\
\
\
\
\
       
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
                                                        
            self_id = id(self)
            key_data = f"{key_prefix}:{func.__name__}:{self_id}:{str(args)}:{str(sorted(kwargs.items()))}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
                                                                   
            if not hasattr(self, '_method_cache'):
                self._method_cache = CacheHelpers()
            
            cache = self._method_cache
            
                                   
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
                                             
            result = func(self, *args, **kwargs)
            cache.set(cache_key, result, ttl_seconds)
            
            return result
        
        return wrapper
    return decorator


                       
cache = CacheHelpers()


def get_cache() -> CacheHelpers:
                                        
    return cache


def cached(ttl_seconds: int = 300, key_func: Optional[Callable] = None):
\
\
\
\
\
\
       
    return cache_result(ttl_seconds, key_func, cache)
