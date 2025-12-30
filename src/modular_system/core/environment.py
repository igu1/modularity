from typing import Any, Dict, List, Optional, Callable
from .registry import Registry
from ..messaging import get_event_bus

class Environment:
    def __init__(self, registry: Registry):
        self._registry, self._bus = registry, get_event_bus()
        self.template_engine = None

    def render_template(self, module_name: str, template_name: str, **context) -> str:
        if not self.template_engine:
            raise RuntimeError("Template engine not initialized")
        return self.template_engine.render(module_name, template_name, **context)

    def get_module(self, name: str) -> Optional[Any]: return self._registry.modules.get(name)
    def get_service(self, name: str) -> Optional[Any]: return self._registry.services.get(name)
    def register_service(self, name: str, service: Any): self._registry.register_service(name, service)
    def add_route(self, pattern: str, method: str, handler: Callable, mod: str):
        self._registry.routes.append((pattern, method, handler))
    def get_routes(self) -> List[tuple]: return self._registry.get_routes()

    def subscribe(self, topic: str, cb: Callable) -> str: return self._bus.subscribe(topic, cb)
    def publish(self, topic: str, data: Dict, src: str) -> bool: return self._bus.publish_event(topic, data, src)

    def __getattr__(self, name: str) -> Any:
        res = self.get_service(name) or self.get_module(name)
        if res is not None: return res
        raise AttributeError(name)

    def get_status(self) -> Dict: return self._registry.get_status()
