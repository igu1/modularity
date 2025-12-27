from typing import Any, Dict, List, Optional, Callable
from .registry import Registry
from ..messaging import get_event_bus


class Environment:
    
    def __init__(self, registry: Registry):
        self._registry = registry
        self._event_bus = get_event_bus()
    
    # Module Access
    def get_module(self, name: str) -> Optional[Any]:
        """Get a loaded module by name."""
        return self._registry.get_module(name)
    
    def get_available_module(self, name: str) -> Optional[Any]:
        """Get an available module class by name."""
        return self._registry.get_available_module(name)
    
    def list_available_modules(self) -> List[str]:
        """Get list of available module names."""
        return self._registry.list_available_modules()
    
    def list_loaded_modules(self) -> List[str]:
        """Get list of loaded module names."""
        return self._registry.list_loaded_modules()
    
    # Service Access
    def get_service(self, name: str) -> Optional[Any]:
        """Get a registered service by name."""
        return self._registry.get_service(name)
    
    def register_service(self, name: str, service: Any):
        """Register a service."""
        return self._registry.register_service(name, service)
    
    def list_services(self) -> List[str]:
        """Get list of registered service names."""
        return self._registry.list_services()
    
    # Route Access
    def get_routes(self) -> List[tuple]:
        """Get all registered routes."""
        return self._registry.get_routes()
    
    def get_module_for_route(self, route_path: str) -> Optional[str]:
        """Get the module name that owns a specific route."""
        return self._registry.get_module_for_route(route_path)
    
    # Event System Access
    def subscribe_to_event(self, event_name: str, module_name: str, callback: Callable):
        """Subscribe to an event."""
        return self._registry.subscribe(event_name, module_name, callback)
    
    def unsubscribe_from_event(self, event_name: str, module_name: str, callback: Optional[Callable] = None):
        """Unsubscribe from an event."""
        return self._registry.unsubscribe(event_name, module_name, callback)
    
    def emit_event(self, event_name: str, data: Optional[Any] = None, source_module: Optional[str] = None):
        """Emit an event."""
        return self._registry.emit(event_name, data, source_module)
    
    def list_event_subscriptions(self) -> Dict[str, List[str]]:
        """List all event subscriptions."""
        return self._registry.list_subscriptions()
    
    # Properties
    @property
    def registry(self) -> Registry:
        """Get the underlying registry."""
        return self._registry
    
    @property
    def logger(self):
        """Get the logger instance."""
        return self._registry.logger
    
    # Magic Methods for convenient access
    def __getitem__(self, key: str) -> Optional[Any]:
        """Allow dictionary-style access to modules."""
        return self.get_module(key)
    
    def __getattr__(self, name: str) -> Any:
        """
        Allow attribute-style access to services and modules.
        
        This method first tries to get a service with the given name,
        then tries to get a module, and finally raises AttributeError.
        """
        # Try services first
        service = self.get_service(name)
        if service is not None:
            return service
        
        # Then try modules
        module = self.get_module(name)
        if module is not None:
            return module
        
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def __contains__(self, name: str) -> bool:
        """Check if a module or service is available."""
        return (self.get_module(name) is not None) or (self.get_service(name) is not None)
    
    def __dir__(self) -> List[str]:
        """Return list of available attributes for autocomplete."""
        attrs = list(self.__dict__.keys())
        attrs.extend(self.list_services())
        attrs.extend(self.list_loaded_modules())
        return sorted(set(attrs))
    
    # Status and Information
    def get_status(self) -> Dict[str, Any]:
        """Get environment status information."""
        return self._registry.get_status()
    
    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific module.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Module information dictionary or None if not found
        """
        module = self.get_module(module_name)
        if not module:
            return None
        
        info = {
            'name': module_name,
            'loaded': True,
            'class_name': module.__class__.__name__,
            'module': module.__class__.__module__
        }
        
        # Add additional info if available
        if hasattr(module, 'get_info'):
            try:
                manifest_info = module.get_info()
                info.update(manifest_info)
            except Exception:
                pass  # Ignore errors getting manifest info
        
        return info
    
    def get_service_info(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service information dictionary or None if not found
        """
        service = self.get_service(service_name)
        if not service:
            return None
        
        return {
            'name': service_name,
            'class_name': service.__class__.__name__,
            'module': service.__class__.__module__
        }
    
    def list_all_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all available resources (modules and services) with their info."""
        resources = {
            'modules': [],
            'services': []
        }
        
        # Module information
        for module_name in self.list_loaded_modules():
            module_info = self.get_module_info(module_name)
            if module_info:
                resources['modules'].append(module_info)
        
        # Service information
        for service_name in self.list_services():
            service_info = self.get_service_info(service_name)
            if service_info:
                resources['services'].append(service_info)
        
        return resources
    
    # Pub/Sub functionality
    def subscribe(self, topic: str, callback: Callable) -> str:
        """Subscribe to a topic with callback."""
        return self._event_bus.subscribe(topic, callback)
    
    def unsubscribe(self, topic: str, subscription_id: str) -> bool:
        """Unsubscribe from a topic."""
        return self._event_bus.unsubscribe(topic, subscription_id)
    
    def publish(self, topic: str, data: Dict[str, Any], source_module: str) -> bool:
        """Publish an event to a topic."""
        return self._event_bus.publish_event(topic, data, source_module)
    
    def send_request(self, topic: str, data: Dict[str, Any], source_module: str, target_module: str) -> bool:
        """Send a request to a specific module."""
        return self._event_bus.send_request(topic, data, source_module, target_module)
    
    def send_response(self, topic: str, data: Dict[str, Any], source_module: str, correlation_id: str) -> bool:
        """Send a response to a request."""
        return self._event_bus.send_response(topic, data, source_module, correlation_id)
    
    def get_event_bus(self):
        """Get the event bus instance."""
        return self._event_bus
