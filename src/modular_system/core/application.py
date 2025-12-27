                                                    

import re
from typing import Optional, Dict, Any, Callable, Tuple
from ..logging.logger import CoreLogger
from .registry import Registry
from .environment import Environment
from ..extensions.patch_engine import PatchEngine


class ModularSystem:
\
\
\
\
\
       
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
\
\
\
\
\
           
        self.config = config or {}
        self.registry = Registry()
        self.env = Environment(self.registry)
        self.logger = CoreLogger()
        self.patch_engine: Optional[PatchEngine] = None
        
        self._load_available_modules()
        self._setup_extensions()
        
        self.logger.log("core", "Modular system initialized", "info")
    
    def _load_available_modules(self):
                                                              
        try:
            from ..modules import modules as available_modules
            self.registry.set_available_modules(available_modules)
            self.logger.log("core", f"Loaded {len(available_modules)} available modules", "info")
        except ImportError as e:
            self.logger.log("core", f"Could not load modules: {e}", "warning")
    
    def load_module(self, module_name: str) -> bool:
        return self.registry.load_module(module_name, self.env)
    
    def get_module(self, module_name: str):
        return self.env.get_module(module_name)
    
    def _match_route(self, route: str, route_pattern: str) -> Tuple[bool, Dict[str, str]]:
        pattern = route_pattern
        pattern = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', pattern)
        pattern = f'^{pattern}$'
        match = re.match(pattern, route)
        if match:
            return True, match.groupdict()
        return False, {}
    
    def _create_handler_with_module(self, handler: Callable,
                                   route_params: Optional[Dict[str, str]] = None) -> Callable:
        def wrapped_handler(environ, start_response):
            environ['ROUTE_PARAMS'] = route_params or {}
            
            if isinstance(handler, str):
                module_path, func_name = handler.rsplit('.', 1)
                handler_module = __import__(module_path, fromlist=[func_name])
                handler_func = getattr(handler_module, func_name)
                return handler_func(environ, start_response, self.env)
            else:
                return handler(environ, start_response, self.env)
        return wrapped_handler
    
    def request_handler(self, environ: Dict[str, Any], start_response: Callable):
\
\
\
\
\
\
\
\
\
           
        route = environ.get('PATH_INFO', '/')
        method = environ['REQUEST_METHOD']
        
        for route_name, route_method, handler in self.env.get_routes():
            matches, params = self._match_route(route, route_name)
            if matches and method == route_method:
                module_name = self.env.get_module_for_route(route_name)
                if module_name:
                    return self._create_handler_with_module(handler, params)(environ, start_response)
                return self._create_handler_with_module(handler, params)(environ, start_response)
        
        return self._404_response(start_response)
    
    def _404_response(self, start_response: Callable):
        start_response('404 Not Found', [('Content-type', 'text/plain')])
        return [b"Page not found"]
    
    def _setup_extensions(self):
        try:
            self.patch_engine = PatchEngine()
            self.patch_engine.set_logger(self.logger)
            
            import os
            extensions_dir = os.path.join(os.path.dirname(__file__), '..', 'extensions')
            if os.path.exists(extensions_dir):
                self.patch_engine.load_patches_from_directory(extensions_dir)
            
            modules_dir = os.path.join(os.path.dirname(__file__), '..', 'modules')
            if os.path.exists(modules_dir):
                for module_name in os.listdir(modules_dir):
                    module_patches_dir = os.path.join(modules_dir, module_name, 'patches')
                    if os.path.exists(module_patches_dir):
                        self.patch_engine.load_patches_from_directory(module_patches_dir)
            
            def apply_patches_hook(module_name: str, module_instance: Any, env: Any):
                if self.patch_engine:
                    applied = self.patch_engine.apply_patches_to_module(module_name, module_instance, env)
                    if applied > 0:
                        self.logger.log("core", f"Applied {applied} patches to module '{module_name}'", "info")
            
            self.registry.register_hook('module_loaded', apply_patches_hook)
            
            patch_count = len(self.patch_engine.patches) if self.patch_engine else 0
            self.logger.log("core", f"Extension system initialized with {patch_count} patches", "info")
            
        except Exception as e:
            self.logger.log("core", f"Error setting up extensions: {e}", "error")
    
    def get_status(self) -> Dict[str, Any]:
                                            
        return {
            'registry': self.registry.get_status(),
            'extensions': self.patch_engine.get_statistics() if self.patch_engine else {}
        }
    
    def run(self, host: str = 'localhost', port: int = 8080, debug: bool = False):
\
\
\
\
\
\
\
           
        from wsgiref.simple_server import make_server
        
        def wsgi_app(environ, start_response):
            return self.request_handler(environ, start_response)
        
        try:
            httpd = make_server(host, port, wsgi_app)
            self.logger.log("core", f"Server running on http://{host}:{port}", "info")
            self.logger.log("core", "Press Ctrl+C to stop the server", "info")
            
            if debug:
                self.logger.log("core", "Debug mode enabled", "info")
            
            httpd.serve_forever()
        except KeyboardInterrupt:
            self.logger.log("core", "Server stopped", "info")
        except Exception as e:
            self.logger.log("core", f"Server error: {e}", "error")
            raise
