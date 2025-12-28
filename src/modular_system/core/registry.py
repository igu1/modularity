from typing import Dict, List, Any, Callable, Set, Tuple, Optional
from ..logging.logger import CoreLogger
class Registry:
    def __init__(self, logger: Optional[CoreLogger] = None):
        self.modules: Dict[str, Any] = {}
        self.services: Dict[str, Any] = {}
        self.routes: List[Tuple[str, str, Callable]] = []
        self.route_to_module: Dict[str, str] = {}
        self.available_modules: Dict[str, Any] = {}
        self._subscribers: Dict[str, Set[Tuple[str, Callable]]] = {}
        self._extension_hooks: Dict[str, List[Callable]] = {}
        self.logger = logger or CoreLogger()
    def register_module(self, name: str, module: Any):
        self.modules[name] = module
        self.logger.log("registry", f"Registered module: {name}", "debug")
    def get_module(self, name: str) -> Optional[Any]:
        return self.modules.get(name)
    def set_available_modules(self, modules_dict: Dict[str, Any]):
        self.available_modules = modules_dict
        self.logger.log("registry", f"Set {len(modules_dict)} available modules", "debug")
    def get_available_module(self, name: str) -> Optional[Any]:
        return self.available_modules.get(name)
    def load_module(self, module_name: str, env: Any) -> bool:
        module_class = self.get_available_module(module_name)
        if not module_class:
            self.logger.log("registry", f"Module '{module_name}' not found in available modules", "warning")
            return False
        self.logger.log("registry", f"Loading module: {module_name}", "info")
        try:
            temp_instance = module_class()
            module_deps = getattr(temp_instance, 'dependencies', [])
            for dep in module_deps:
                if dep not in self.list_loaded_modules() and dep in self.list_available_modules():
                    if not self.load_module(dep, env):
                        raise RuntimeError(f"Failed to load dependency: {dep}")
                elif dep not in self.list_loaded_modules():
                    error_msg = f"Module '{dep}' is not available but listed as dependency"
                    self.logger.log("registry", error_msg, "error")
                    raise ValueError(error_msg)
            module_instance = module_class()
            if hasattr(module_instance, 'initialize'):
                module_instance.initialize(env)
            
            try:
                routes = module_instance.load_routes()
                self.add_routes(routes, module_name)
            except AttributeError:
                pass
            
            self.register_module(module_name, module_instance)
            self._trigger_hook('module_loaded', module_name, module_instance, env)
            self.logger.log("registry", f"Successfully loaded module: {module_name}", "info")
            return True
        except Exception as e:
            self.logger.log("registry", f"Error loading module {module_name}: {e}", "error")
            import traceback
            self.logger.log("registry", f"Traceback: {traceback.format_exc()}", "error")
            return False
    def list_available_modules(self) -> List[str]:
        return list(self.available_modules.keys())
    def list_loaded_modules(self) -> List[str]:
        return list(self.modules.keys())
    def register_service(self, name: str, service: Any):
        self.services[name] = service
        self.logger.log("registry", f"Registered service: {name}", "debug")
    def get_service(self, name: str) -> Optional[Any]:
        return self.services.get(name)
    def list_services(self) -> List[str]:
        return list(self.services.keys())
    def add_routes(self, routes: Any, module_name: Optional[str] = None):
        if isinstance(routes, list):
            self.routes.extend(routes)
            if module_name:
                for route in routes:
                    if isinstance(route, tuple) and len(route) >= 3:
                        route_path = route[0]
                        self.route_to_module[route_path] = module_name
        else:
            self.routes.append(routes)
            if module_name and isinstance(routes, tuple) and len(routes) >= 3:
                route_path = routes[0]
                self.route_to_module[route_path] = module_name
        self.logger.log("registry", f"Added routes for module: {module_name}", "debug")
    def get_routes(self) -> List[Tuple[str, str, Callable]]:
        return self.routes
    def clear_routes(self):
        self.routes = []
        self.route_to_module = {}
        self.logger.log("registry", "Cleared all routes", "debug")
    def get_module_for_route(self, route_path: str) -> Optional[str]:
        return self.route_to_module.get(route_path)
    def subscribe(self, event_name: str, module_name: str, callback_func: Callable):
        if event_name not in self._subscribers:
            self._subscribers[event_name] = set()
        self._subscribers[event_name].add((module_name, callback_func))
        self.logger.log("registry", f"Module '{module_name}' subscribed to event '{event_name}'", "info")
    def unsubscribe(self, event_name: str, module_name: str, callback_func: Optional[Callable] = None):
        if event_name not in self._subscribers:
            return
        if callback_func:
            self._subscribers[event_name].discard((module_name, callback_func))
        else:
            self._subscribers[event_name] = {
                (mod, callback) for mod, callback in self._subscribers[event_name]
                if mod != module_name
            }
        self.logger.log("registry", f"Module '{module_name}' unsubscribed from event '{event_name}'", "info")
    def emit(self, event_name: str, data: Optional[Any] = None, source_module: Optional[str] = None):
        if event_name not in self._subscribers:
            return
        event_data = {
            'event_name': event_name,
            'data': data,
            'source': source_module,
            'timestamp': __import__('datetime').datetime.utcnow().isoformat()
        }
        subscriber_count = len(self._subscribers[event_name])
        self.logger.log("registry", 
                       f"Emitting event '{event_name}' from '{source_module}' to {subscriber_count} subscribers", 
                       "info")
        if hasattr(self.logger, 'log_event'):
            self.logger.log_event(event_data)
        for module_name, callback_func in self._subscribers[event_name]:
            try:
                module = self.get_module(module_name)
                if module:
                    callback_func(event_data)
                else:
                    self.logger.log("registry", 
                                   f"Warning: Module '{module_name}' not found for event '{event_name}'", 
                                   "warning")
            except Exception as e:
                self.logger.log("registry", 
                               f"Error in event handler for '{event_name}' in module '{module_name}': {e}", 
                               "error")
    def list_subscriptions(self) -> Dict[str, List[str]]:
        subscriptions = {}
        for event_name, subscribers in self._subscribers.items():
            subscriptions[event_name] = [module_name for module_name, _ in subscribers]
        return subscriptions
    def register_hook(self, hook_name: str, callback: Callable):
        if hook_name not in self._extension_hooks:
            self._extension_hooks[hook_name] = []
        self._extension_hooks[hook_name].append(callback)
        self.logger.log("registry", f"Registered hook: {hook_name}", "debug")
    def _trigger_hook(self, hook_name: str, *args, **kwargs):
        if hook_name in self._extension_hooks:
            for callback in self._extension_hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    self.logger.log("registry", f"Error in hook '{hook_name}': {e}", "error")
    def get_status(self) -> Dict[str, Any]:
        return {
            'loaded_modules': len(self.modules),
            'available_modules': len(self.available_modules),
            'services': len(self.services),
            'routes': len(self.routes),
            'event_subscriptions': sum(len(subs) for subs in self._subscribers.values()),
            'active_hooks': len(self._extension_hooks)
        }
