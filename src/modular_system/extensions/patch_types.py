from typing import Any, Dict, Optional, Callable

class Patch:
    def __init__(self, name: str, desc: str = ""):
        self.name, self.desc, self.target = name, desc, None

    def apply(self, inst: Any, env: Any): 
        pass

class FunctionPatch(Patch):
    def __init__(self, name: str, func_name: str, new_func: Callable, desc: str = ""):
        super().__init__(name, desc)
        self.func_name, self.new_func = func_name, new_func

    def apply(self, inst: Any, env: Any):
        if hasattr(inst, self.func_name): 
            setattr(inst, self.func_name, self.new_func)

class ServicePatch(Patch):
    def __init__(self, name: str, svc_name: str, svc_inst: Any, desc: str = ""):
        super().__init__(name, desc)
        self.svc_name, self.svc_inst = svc_name, svc_inst

    def apply(self, inst: Any, env: Any):
        if hasattr(env, 'register_service'): 
            env.register_service(self.svc_name, self.svc_inst)

class ModelPatch(Patch):
    def __init__(self, name: str, model_name: str, new_model: Any, desc: str = ""):
        super().__init__(name, desc)
        self.model_name, self.new_model = model_name, new_model

    def apply(self, inst: Any, env: Any):
        if hasattr(inst, 'models'): 
            setattr(inst.models, self.model_name, self.new_model)

class FieldPatch(Patch):
    def __init__(self, name: str, model_name: str, field_name: str, new_field: Any, desc: str = ""):
        super().__init__(name, desc)
        self.model_name, self.field_name, self.new_field = model_name, field_name, new_field

    def apply(self, inst: Any, env: Any):
        m = getattr(inst, self.model_name, None) or getattr(getattr(inst, 'models', None), self.model_name, None)
        if m: 
            setattr(m, self.field_name, self.new_field)

class RoutePatch(Patch):
    def __init__(self, name: str, pattern: str, method: str, handler: Callable, mod: str, desc: str = ""):
        super().__init__(name, desc)
        self.pattern, self.method, self.handler, self.mod = pattern, method, handler, mod

    def apply(self, inst: Any, env: Any):
        if hasattr(env, 'add_route'): 
            env.add_route(self.pattern, self.method, self.handler, self.mod)

class ConfigPatch(Patch):
    def __init__(self, name: str, updates: Dict[str, Any], desc: str = ""):
        super().__init__(name, desc)
        self.updates = updates

    def apply(self, inst: Any, env: Any):
        if hasattr(inst, 'config'): 
            inst.config.update(self.updates)
