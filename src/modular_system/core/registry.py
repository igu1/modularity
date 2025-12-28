from typing import Dict, List, Any, Callable, Tuple, Optional
from ..logging.logger import CoreLogger

class Registry:
    def __init__(self, config: Dict = None, logger: CoreLogger = None):
        self.modules, self.services, self.routes = {}, {}, []
        self.avail, self.subs, self.hooks = {}, {}, {}
        self.logger, self.config = logger or CoreLogger(), config or {}

    def set_available_modules(self, mods: Dict): self.avail = mods

    def load_module(self, name: str, env: Any) -> bool:
        cls = self.avail.get(name)
        if not cls: return False
        try:
            cfg = self.config.get('modules', {}).get(name, self.config)
            inst = cls(config=cfg)
            for d in getattr(inst, 'dependencies', []):
                if d not in self.modules and not self.load_module(d, env): return False
            if hasattr(inst, 'initialize'): inst.initialize(env)
            if hasattr(inst, 'load_routes'): self.routes.extend(inst.load_routes())
            self.modules[name] = inst
            self._trigger('module_loaded', name, inst, env)
            return True
        except Exception as e:
            self.logger.log("registry", f"Load fail {name}: {e}", "error")
            return False

    def register_service(self, name: str, svc: Any): self.services[name] = svc
    def get_service(self, name: str) -> Optional[Any]: return self.services.get(name)
    def get_routes(self) -> List[Tuple]: return self.routes

    def subscribe(self, evt: str, mod: str, cb: Callable): self.subs.setdefault(evt, set()).add((mod, cb))
    def emit(self, name: str, data: Any = None, src: str = None):
        if name not in self.subs: return
        e = {'name': name, 'data': data, 'src': src, 'ts': __import__('datetime').datetime.now().isoformat()}
        for mod, cb in self.subs[name]:
            try:
                if mod in self.modules: cb(e)
            except: pass

    def register_hook(self, name: str, cb: Callable): self.hooks.setdefault(name, []).append(cb)
    def _trigger(self, name: str, *args, **kwargs):
        for cb in self.hooks.get(name, []):
            try: cb(*args, **kwargs)
            except: pass

    def get_status(self) -> Dict:
        return {'mods': len(self.modules), 'avail': len(self.avail), 'svcs': len(self.services), 'routes': len(self.routes)}
