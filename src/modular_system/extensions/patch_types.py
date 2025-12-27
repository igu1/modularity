"""Patch types for the extension system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable


class Patch(ABC):
    """
    Base class for all patch types.
    
    A patch represents a modification that can be applied to a module
    to extend or modify its behavior.
    """
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize patch.
        
        Args:
            name: Unique name for the patch
            description: Human-readable description of the patch
        """
        self.name = name
        self.description = description
        self.target_module: Optional[str] = None
    
    @abstractmethod
    def apply(self, module_instance: Any, env: Any):
        """
        Apply the patch to a module instance.
        
        Args:
            module_instance: The module instance to patch
            env: Environment object
        """
        pass


class FunctionPatch(Patch):
    """
    Patch that replaces or modifies a function in a module.
    
    Used to change the behavior of existing functions or add new ones.
    """
    
    def __init__(self, name: str, function_name: str, new_function: Callable, 
                 description: str = ""):
        """
        Initialize function patch.
        
        Args:
            name: Patch name
            function_name: Name of the function to replace
            new_function: New function to use
            description: Patch description
        """
        super().__init__(name, description)
        self.function_name = function_name
        self.new_function = new_function
    
    def apply(self, module_instance: Any, env: Any):
        """Apply the function patch."""
        if hasattr(module_instance, self.function_name):
            setattr(module_instance, self.function_name, self.new_function)


class ServicePatch(Patch):
    """
    Patch that adds or replaces a service in the module system.
    
    Services are shared components that modules can use to access
    common functionality like database connections, caching, etc.
    """
    
    def __init__(self, name: str, service_name: str, service_instance: Any,
                 description: str = ""):
        """
        Initialize service patch.
        
        Args:
            name: Patch name
            service_name: Name of the service
            service_instance: Service instance
            description: Patch description
        """
        super().__init__(name, description)
        self.service_name = service_name
        self.service_instance = service_instance
    
    def apply(self, module_instance: Any, env: Any):
        """Apply the service patch."""
        if hasattr(env, 'register_service'):
            env.register_service(self.service_name, self.service_instance)


class ModelPatch(Patch):
    """
    Patch that adds or modifies a data model in a module.
    
    Used to extend the data model with new fields or relationships.
    """
    
    def __init__(self, name: str, model_name: str, new_model: Any,
                 description: str = ""):
        """
        Initialize model patch.
        
        Args:
            name: Patch name
            model_name: Name of the model to modify
            new_model: New model definition
            description: Patch description
        """
        super().__init__(name, description)
        self.model_name = model_name
        self.new_model = new_model
    
    def apply(self, module_instance: Any, env: Any):
        """Apply the model patch."""
        if hasattr(module_instance, 'models'):
            setattr(module_instance.models, self.model_name, self.new_model)


class FieldPatch(Patch):
    """
    Patch that adds or modifies a field in a data model.
    
    Used to add new fields to existing models or modify field properties.
    """
    
    def __init__(self, name: str, model_name: str, field_name: str, 
                 new_field: Any, description: str = ""):
        """
        Initialize field patch.
        
        Args:
            name: Patch name
            model_name: Name of the target model
            field_name: Name of the field to modify
            new_field: New field definition
            description: Patch description
        """
        super().__init__(name, description)
        self.model_name = model_name
        self.field_name = field_name
        self.new_field = new_field
    
    def apply(self, module_instance: Any, env: Any):
        """Apply the field patch."""
        if hasattr(module_instance, self.model_name):
            model = getattr(module_instance, self.model_name)
            setattr(model, self.field_name, self.new_field)


class RoutePatch(Patch):
    """
    Patch that adds or modifies a route in a module.
    
    Used to add new endpoints or change existing route handlers.
    """
    
    def __init__(self, name: str, route_pattern: str, method: str, 
                 handler: Callable, module_name: str, description: str = ""):
        """
        Initialize route patch.
        
        Args:
            name: Patch name
            route_pattern: URL pattern for the route
            method: HTTP method (GET, POST, etc.)
            handler: Handler function for the route
            module_name: Name of the module providing the route
            description: Patch description
        """
        super().__init__(name, description)
        self.route_pattern = route_pattern
        self.method = method
        self.handler = handler
        self.module_name = module_name
    
    def apply(self, module_instance: Any, env: Any):
        """Apply the route patch."""
        if hasattr(env, 'add_route'):
            env.add_route(self.route_pattern, self.method, self.handler, self.module_name)


class ConfigPatch(Patch):
    """
    Patch that modifies module configuration.
    
    Used to update configuration values or add new config options.
    """
    
    def __init__(self, name: str, config_updates: Dict[str, Any], 
                 description: str = ""):
        """
        Initialize configuration patch.
        
        Args:
            name: Patch name
            config_updates: Dictionary of configuration updates
            description: Patch description
        """
        super().__init__(name, description)
        self.config_updates = config_updates
    
    def apply(self, module_instance: Any, env: Any):
        """Apply the configuration patch."""
        if hasattr(module_instance, 'config'):
            module_instance.config.update(self.config_updates)


class TemplatePatch(Patch):
    """
    Patch that adds or modifies templates in a module.
    
    Used to add new template files or modify existing ones.
    """
    
    def __init__(self, name: str, template_name: str, template_content: str,
                 description: str = ""):
        """
        Initialize template patch.
        
        Args:
            name: Patch name
            template_name: Name of the template
            template_content: Template content
            description: Patch description
        """
        super().__init__(name, description)
        self.template_name = template_name
        self.template_content = template_content
    
    def apply(self, module_instance: Any, env: Any):
        """Apply the template patch."""
        if hasattr(module_instance, 'templates'):
            module_instance.templates[self.template_name] = self.template_content
