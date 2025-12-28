import time, sys, psutil
from datetime import datetime

class SystemService:
    def __init__(self, mod):
        self.mod, self.start = mod, time.time()

    def get_system_status(self):
        reg = getattr(self.mod.env, '_registry', None)
        pe = getattr(self.mod.env, '_patch_engine', None)
        return {
            'modules': list(reg.modules.keys()) if reg else [],
            'routes': len(reg.routes) if reg else 0,
            'patches': len(pe.applied) if pe else 0,
            'uptime': self._uptime(),
            'mem': self._mem(),
            'py': f"{sys.version_info.major}.{sys.version_info.minor}",
            'ts': str(datetime.now())
        }

    def _uptime(self):
        s = int(time.time() - self.start)
        h, m = divmod(s, 3600); m, s = divmod(m, 60)
        return f"{h}h {m}m {s}s" if h else (f"{m}m {s}s" if m else f"{s}s")

    def _mem(self):
        try:
            p = psutil.Process()
            m = p.memory_info()
            return {'rss': round(m.rss/1024/1024, 2), 'pct': round(p.memory_percent(), 2)}
        except: return {}
