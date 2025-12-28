from typing import Any, Dict, List, Optional, Callable
from .registry import Registry
from ..messaging import get_event_bus

class Environment:
    def __init__(self, registry: Registry):
        self._registry, self._bus = registry, get_event_bus()

    def get_module(self, name: str) -> Optional[Any]: return self._registry.modules.get(name)
    def get_service(self, name: str) -> Optional[Any]: return self._registry.services.get(name)
    def register_service(self, name: str, service: Any): self._registry.register_service(name, service)
    def get_routes(self) -> List[tuple]: return self._registry.get_routes()

    def subscribe(self, topic: str, cb: Callable) -> str: return self._bus.subscribe(topic, cb)
    def publish(self, topic: str, data: Dict, src: str) -> bool: return self._bus.publish_event(topic, data, src)

    def __getattr__(self, name: str) -> Any:
        res = self.get_service(name) or self.get_module(name)
        if res is not None: return res
        raise AttributeError(name)

    def get_status(self) -> Dict: return self._registry.get_status()
