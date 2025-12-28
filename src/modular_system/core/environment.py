from typing import Any, Dict, List, Optional, Callable
from .registry import Registry
from ..messaging import get_event_bus
class Environment:
    def __init__(self, registry: Registry):
        self._registry = registry
        self._event_bus = get_event_bus()
    def get_module(self, name: str) -> Optional[Any]:
        return self._registry.get_module(name)
    def get_available_module(self, name: str) -> Optional[Any]:
        return self._registry.get_available_module(name)
    def list_available_modules(self) -> List[str]:
        return self._registry.list_available_modules()
    def list_loaded_modules(self) -> List[str]:
        return self._registry.list_loaded_modules()
    def get_service(self, name: str) -> Optional[Any]:
        return self._registry.get_service(name)
    def register_service(self, name: str, service: Any):
        return self._registry.register_service(name, service)
    def list_services(self) -> List[str]:
        return self._registry.list_services()
    def get_routes(self) -> List[tuple]:
        return self._registry.get_routes()
    def get_module_for_route(self, route_path: str) -> Optional[str]:
        return self._registry.get_module_for_route(route_path)
    def subscribe_to_event(self, event_name: str, module_name: str, callback: Callable):
        return self._registry.subscribe(event_name, module_name, callback)
    def unsubscribe_from_event(self, event_name: str, module_name: str, callback: Optional[Callable] = None):
        return self._registry.unsubscribe(event_name, module_name, callback)
    def emit_event(self, event_name: str, data: Optional[Any] = None, source_module: Optional[str] = None):
        return self._registry.emit(event_name, data, source_module)
    def list_event_subscriptions(self) -> Dict[str, List[str]]:
        return self._registry.list_subscriptions()
    @property
    def registry(self) -> Registry:
        return self._registry
    @property
    def logger(self):
        return self._registry.logger
    def __getitem__(self, key: str) -> Optional[Any]:
        return self.get_module(key)
    def __getattr__(self, name: str) -> Any:
        service = self.get_service(name)
        if service is not None:
            return service
        module = self.get_module(name)
        if module is not None:
            return module
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    def __contains__(self, name: str) -> bool:
        return (self.get_module(name) is not None) or (self.get_service(name) is not None)
    def __dir__(self) -> List[str]:
        attrs = list(self.__dict__.keys())
        attrs.extend(self.list_services())
        attrs.extend(self.list_loaded_modules())
        return sorted(set(attrs))
    def get_status(self) -> Dict[str, Any]:
        return self._registry.get_status()
    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        module = self.get_module(module_name)
        if not module:
            return None
        info = {
            'name': module_name,
            'loaded': True,
            'class_name': module.__class__.__name__,
            'module': module.__class__.__module__
        }
        if hasattr(module, 'get_info'):
            try:
                manifest_info = module.get_info()
                info.update(manifest_info)
            except Exception:
                pass                                       
        return info
    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        service = self.get_service(service_name)
        if not service:
            return None
        return {
            'name': service_name,
            'class_name': service.__class__.__name__,
            'module': service.__class__.__module__
        }
    def list_all_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        resources = {
            'modules': [],
            'services': []
        }
        for module_name in self.list_loaded_modules():
            module_info = self.get_module_info(module_name)
            if module_info:
                resources['modules'].append(module_info)
        for service_name in self.list_services():
            service_info = self.get_service_info(service_name)
            if service_info:
                resources['services'].append(service_info)
        return resources
    def subscribe(self, topic: str, callback: Callable) -> str:
        return self._event_bus.subscribe(topic, callback)
    def unsubscribe(self, topic: str, subscription_id: str) -> bool:
        return self._event_bus.unsubscribe(topic, subscription_id)
    def publish(self, topic: str, data: Dict[str, Any], source_module: str) -> bool:
        return self._event_bus.publish_event(topic, data, source_module)
    def send_request(self, topic: str, data: Dict[str, Any], source_module: str, target_module: str) -> bool:
        return self._event_bus.send_request(topic, data, source_module, target_module)
    def send_response(self, topic: str, data: Dict[str, Any], source_module: str, correlation_id: str) -> bool:
        return self._event_bus.send_response(topic, data, source_module, correlation_id)
    def get_event_bus(self):
        return self._event_bus
