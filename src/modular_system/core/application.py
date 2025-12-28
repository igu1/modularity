import re, os, mimetypes
from typing import Optional, Dict, Any, Callable, Tuple
from ..logging.logger import CoreLogger
from .templating import TemplateEngine
from .registry import Registry
from .environment import Environment
from ..extensions.patch_engine import PatchEngine

class ModularSystem:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config, self.logger = config or {}, CoreLogger()
        self.registry = Registry(config=self.config, logger=self.logger)
        
        modules_path = os.path.join(os.path.dirname(__file__), '..', 'modules')
        self.template_engine = TemplateEngine(modules_path)
        
        self.env = Environment(self.registry)
        self.env.template_engine = self.template_engine
        self.patch_engine: Optional[PatchEngine] = None
        self._load_mods()
        self._setup_exts()

    def _load_mods(self):
        try:
            from ..modules import modules
            self.registry.set_available_modules(modules)
        except: pass

    def load_module(self, name: str) -> bool: return self.registry.load_module(name, self.env)

    def _match(self, path: str, pattern: str) -> Tuple[bool, Dict[str, str]]:
        m = re.match(f"^{re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', pattern)}$", path)
        return (True, m.groupdict()) if m else (False, {})

    def handle(self, env: Dict, start: Callable):
        path, method = env.get('PATH_INFO', '/'), env['REQUEST_METHOD']
        if not path.startswith('/'): path = '/' + path
        
        self.logger.log("core", f"Handling {method} {path}", "debug")
        
        if path.startswith('/static/'):
            parts = path.split('/')
            if len(parts) >= 4:
                module_name = parts[2]
                filename = '/'.join(parts[3:])
                base = os.path.join(os.path.dirname(__file__), '..', 'modules', module_name, 'static')
                file_path = os.path.join(base, filename)
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    self.logger.log("core", f"Serving static file: {file_path}", "debug")
                    mime_type, _ = mimetypes.guess_type(file_path)
                    mime_type = mime_type or 'application/octet-stream'
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    start('200 OK', [('Content-Type', mime_type), ('Content-Length', str(len(content)))])
                    return [content]

        routes = self.registry.get_routes()
        self.logger.log("core", f"Checking {len(routes)} routes", "debug")
        for route, r_method, handler in routes:
            ok, params = self._match(path, route)
            if ok and method == r_method:
                self.logger.log("core", f"Matched route: {route}", "debug")
                env['ROUTE_PARAMS'] = params
                return handler(env, start, self.env) if not isinstance(handler, str) else \
                       getattr(__import__(handler.rsplit('.', 1)[0], fromlist=[handler.rsplit('.', 1)[1]]), handler.rsplit('.', 1)[1])(env, start, self.env)

        self.logger.log("core", f"No route matched for {path}", "warning")
        start('404 Not Found', [('Content-type', 'text/plain')])
        return [b"Not Found"]

    def _setup_exts(self):
        self.patch_engine = PatchEngine()
        self.patch_engine.set_logger(self.logger)
        base = os.path.join(os.path.dirname(__file__), '..')
        for d in [os.path.join(base, 'extensions'), os.path.join(base, 'modules')]:
            if not os.path.exists(d): continue
            if 'modules' in d:
                for m in os.listdir(d):
                    p = os.path.join(d, m, 'patches')
                    if os.path.exists(p): self.patch_engine.load_patches_from_directory(p)
            else: self.patch_engine.load_patches_from_directory(d)
        self.registry.register_hook('module_loaded', lambda n, i, e: self.patch_engine.apply_patches_to_module(n, i, e) if self.patch_engine else 0)

    def run(self, host: str = 'localhost', port: int = 8080):
        from wsgiref.simple_server import make_server
        self.logger.log("core", f"Serving on {host}:{port}", "info")
        make_server(host, port, self.handle).serve_forever()
