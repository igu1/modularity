                                           

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable


class Patch(ABC):
\
\
\
\
\
       
    
    def __init__(self, name: str, description: str = ""):
\
\
\
\
\
\
           
        self.name = name
        self.description = description
        self.target_module: Optional[str] = None
    
    @abstractmethod
    def apply(self, module_instance: Any, env: Any):
\
\
\
\
\
\
           
        pass


class FunctionPatch(Patch):
\
\
\
\
       
    
    def __init__(self, name: str, function_name: str, new_function: Callable, 
                 description: str = ""):
\
\
\
\
\
\
\
\
           
        super().__init__(name, description)
        self.function_name = function_name
        self.new_function = new_function
    
    def apply(self, module_instance: Any, env: Any):
                                       
        if hasattr(module_instance, self.function_name):
            setattr(module_instance, self.function_name, self.new_function)


class ServicePatch(Patch):
\
\
\
\
\
       
    
    def __init__(self, name: str, service_name: str, service_instance: Any,
                 description: str = ""):
\
\
\
\
\
\
\
\
           
        super().__init__(name, description)
        self.service_name = service_name
        self.service_instance = service_instance
    
    def apply(self, module_instance: Any, env: Any):
                                      
        if hasattr(env, 'register_service'):
            env.register_service(self.service_name, self.service_instance)


class ModelPatch(Patch):
\
\
\
\
       
    
    def __init__(self, name: str, model_name: str, new_model: Any,
                 description: str = ""):
\
\
\
\
\
\
\
\
           
        super().__init__(name, description)
        self.model_name = model_name
        self.new_model = new_model
    
    def apply(self, module_instance: Any, env: Any):
                                    
        if hasattr(module_instance, 'models'):
            setattr(module_instance.models, self.model_name, self.new_model)


class FieldPatch(Patch):
\
\
\
\
       
    
    def __init__(self, name: str, model_name: str, field_name: str, 
                 new_field: Any, description: str = ""):
\
\
\
\
\
\
\
\
\
           
        super().__init__(name, description)
        self.model_name = model_name
        self.field_name = field_name
        self.new_field = new_field
    
    def apply(self, module_instance: Any, env: Any):
                                    
        if hasattr(module_instance, self.model_name):
            model = getattr(module_instance, self.model_name)
            setattr(model, self.field_name, self.new_field)


class RoutePatch(Patch):
\
\
\
\
       
    
    def __init__(self, name: str, route_pattern: str, method: str, 
                 handler: Callable, module_name: str, description: str = ""):
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
           
        super().__init__(name, description)
        self.route_pattern = route_pattern
        self.method = method
        self.handler = handler
        self.module_name = module_name
    
    def apply(self, module_instance: Any, env: Any):
                                    
        if hasattr(env, 'add_route'):
            env.add_route(self.route_pattern, self.method, self.handler, self.module_name)


class ConfigPatch(Patch):
\
\
\
\
       
    
    def __init__(self, name: str, config_updates: Dict[str, Any], 
                 description: str = ""):
\
\
\
\
\
\
\
           
        super().__init__(name, description)
        self.config_updates = config_updates
    
    def apply(self, module_instance: Any, env: Any):
                                            
        if hasattr(module_instance, 'config'):
            module_instance.config.update(self.config_updates)


class TemplatePatch(Patch):
\
\
\
\
       
    
    def __init__(self, name: str, template_name: str, template_content: str,
                 description: str = ""):
\
\
\
\
\
\
\
\
           
        super().__init__(name, description)
        self.template_name = template_name
        self.template_content = template_content
    
    def apply(self, module_instance: Any, env: Any):
                                       
        if hasattr(module_instance, 'templates'):
            module_instance.templates[self.template_name] = self.template_content
