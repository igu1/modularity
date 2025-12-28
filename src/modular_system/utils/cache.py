import hashlib, pickle, os
from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from functools import wraps

class Cache:
    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._expiry: Dict[str, Optional[datetime]] = {}

    def get(self, key: str, default: Any = None) -> Any:
        if key not in self._cache: return default
        if (exp := self._expiry.get(key)) and exp <= datetime.now():
            self.delete(key); return default
        return self._cache[key]

    def set(self, key: str, val: Any, ttl: int = None):
        self._cache[key] = val
        self._expiry[key] = datetime.now() + timedelta(seconds=ttl) if ttl else None

    def delete(self, key: str):
        self._cache.pop(key, None); self._expiry.pop(key, None)

    def clear(self):
        self._cache.clear(); self._expiry.clear()

class FileCache:
    def __init__(self, path: str = 'cache'):
        self.path = path; os.makedirs(path, exist_ok=True)

    def _path(self, key: str) -> str:
        return os.path.join(self.path, hashlib.md5(key.encode()).hexdigest() + ".cache")

    def get(self, key: str, default: Any = None) -> Any:
        p = self._path(key)
        if not os.path.exists(p): return default
        try:
            with open(p, 'rb') as f: data = pickle.load(f)
            if data.get('exp') and data['exp'] <= datetime.now():
                os.remove(p); return default
            return data.get('val')
        except: return default

    def set(self, key: str, val: Any, ttl: int = None):
        try:
            with open(self._path(key), 'wb') as f:
                pickle.dump({'val': val, 'exp': datetime.now() + timedelta(seconds=ttl) if ttl else None}, f)
        except: pass

def cached(ttl: int = 300, cache_inst: Cache = None):
    c = cache_inst or _global_cache
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            k = hashlib.md5(f"{f.__name__}:{args}:{sorted(kwargs.items())}".encode()).hexdigest()
            if (res := c.get(k)) is not None: return res
            res = f(*args, **kwargs)
            c.set(k, res, ttl); return res
        return wrapper
    return decorator

_global_cache = Cache()
def get_cache(): return _global_cache
