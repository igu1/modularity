"""Main application class for the modular system."""

import re
from typing import Optional, Dict, Any, Callable, Tuple
from ..logging.logger import CoreLogger
from .registry import Registry
from .environment import Environment
from ..extensions.patch_engine import PatchEngine


class ModularSystem:
    """
    Main application class that orchestrates the entire modular system.
    
    This class manages module loading, routing, extensions, and provides
    the central entry point for the web application.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the modular system.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.registry = Registry()
        self.env = Environment(self.registry)
        self.logger = CoreLogger()
        self.patch_engine: Optional[PatchEngine] = None
        
        # Load available modules
        self._load_available_modules()
        
        # Setup extensions and patches
        self._setup_extensions()
        
        self.logger.log("core", "Modular system initialized", "info")
    
    def _load_available_modules(self):
        """Load available modules from the modules package."""
        try:
            from ..modules import modules as available_modules
            self.registry.set_available_modules(available_modules)
            self.logger.log("core", f"Loaded {len(available_modules)} available modules", "info")
        except ImportError as e:
            self.logger.log("core", f"Could not load modules: {e}", "warning")
    
    def load_module(self, module_name: str) -> bool:
        """
        Load a module by name.
        
        Args:
            module_name: Name of the module to load
            
        Returns:
            True if module was loaded successfully, False otherwise
        """
        return self.registry.load_module(module_name, self.env)
    
    def get_module(self, module_name: str):
        """Get a loaded module by name."""
        return self.env.get_module(module_name)
    
    def load_manifest(self):
        """Load manifests for all loaded modules."""
        loaded_modules = self.env.list_loaded_modules()
        for name in loaded_modules:
            module = self.env.get_module(name)
            if hasattr(module, 'get_info'):
                try:
                    manifest = module.get_info()
                    self.logger.log("core", f"Loaded manifest for module '{name}'", "debug")
                except Exception as e:
                    self.logger.log("core", f"Error loading manifest for '{name}': {e}", "error")
    
    def _match_route(self, route: str, route_pattern: str) -> Tuple[bool, Dict[str, str]]:
        """
        Match a route against a pattern with parameters.
        
        Args:
            route: The actual route path
            route_pattern: The pattern to match against
            
        Returns:
            Tuple of (matches, parameters_dict)
        """
        pattern = route_pattern
        pattern = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', pattern)
        pattern = f'^{pattern}$'
        match = re.match(pattern, route)
        if match:
            return True, match.groupdict()
        return False, {}
    
    def _create_handler_with_module(self, handler: Callable, module_instance: Any, 
                                   route_params: Optional[Dict[str, str]] = None) -> Callable:
        """
        Create a WSGI handler with module context.
        
        Args:
            handler: The handler function or string path
            module_instance: The module instance to pass to handler
            route_params: Route parameters from URL matching
            
        Returns:
            WSGI handler function
        """
        def wrapped_handler(environ, start_response):
            environ['ROUTE_PARAMS'] = route_params or {}
            
            # If handler is a string path, import it
            if isinstance(handler, str):
                module_path, func_name = handler.rsplit('.', 1)
                handler_module = __import__(module_path, fromlist=[func_name])
                handler_func = getattr(handler_module, func_name)
                return handler_func(environ, start_response, module_instance)
            else:
                return handler(environ, start_response, module_instance)
        return wrapped_handler
    
    def request_handler(self, environ: Dict[str, Any], start_response: Callable):
        """
        Main WSGI request handler.
        
        Args:
            environ: WSGI environment dictionary
            start_response: WSGI start response callable
            
        Returns:
            Response body as list of bytes
        """
        route = environ.get('PATH_INFO', '/')
        method = environ['REQUEST_METHOD']
        
        # Try to match routes
        for route_name, route_method, handler in self.env.get_routes():
            matches, params = self._match_route(route, route_name)
            if matches and method == route_method:
                module_name = self.env.get_module_for_route(route_name)
                if module_name:
                    module_instance = self.env.get_module(module_name)
                    return self._create_handler_with_module(handler, module_instance, params)(environ, start_response)
                return self._create_handler_with_module(handler, None, params)(environ, start_response)
        
        # No route matched, return 404
        return self._404_response(start_response)
    
    def _404_response(self, start_response: Callable):
        """Return a 404 Not Found response."""
        start_response('404 Not Found', [('Content-type', 'text/plain')])
        return [b"Page not found"]
    
    def _setup_extensions(self):
        """Setup the patch/extension system."""
        try:
            self.patch_engine = PatchEngine()
            self.patch_engine.set_logger(self.logger)
            
            # Load patches from extensions directory
            import os
            extensions_dir = os.path.join(os.path.dirname(__file__), '..', 'extensions')
            if os.path.exists(extensions_dir):
                self.patch_engine.load_patches_from_directory(extensions_dir)
            
            # Register hook for applying patches to modules
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
        """Get system status information."""
        return {
            'registry': self.registry.get_status(),
            'extensions': self.patch_engine.get_statistics() if self.patch_engine else {}
        }
    
    def run(self, host: str = 'localhost', port: int = 8080, debug: bool = False):
        """
        Run the development server.
        
        Args:
            host: Host to bind to
            port: Port to bind to
            debug: Enable debug mode
        """
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
