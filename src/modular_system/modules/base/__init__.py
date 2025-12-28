from typing import Dict, Any, List, Optional
from datetime import datetime
import time
class BaseModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = 'base'
        self.version = '1.0.0'
        self._dependencies = []
        self.env = None
        from modular_system.logging.logger import CoreLogger
        self.logger = CoreLogger()
        self.web_views = None
        self.api_views = None
        self.services = None
        self._init_database()
        self.logger.log("base", "Base module initialized", "info")
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    def initialize(self, env):
        self.env = env
        from .views import WebViews, APIViews
        from .services import SystemService
        self.web_views = WebViews(self)
        self.api_views = APIViews(self)
        self.services = {'system_service': SystemService(self)}
        from .routes import get_routes
        routes = get_routes(self)
        for route_pattern, method, handler in routes:
            if hasattr(env, '_registry'):
                env._registry.add_routes([(route_pattern, method, handler)], 'base')
        self.logger.log("base", "Base module initialized with environment", "info")
    def _init_database(self):
        try:
            from modular_system.database.connection import init_db
            if hasattr(self.config, 'get'):
                db_config = self.config.get('database', {})
            elif hasattr(self.config, 'database'):
                db_config = self.config.database
            else:
                db_config = None
            if db_config:
                if hasattr(db_config, 'url'):
                    db_url = db_config.url
                elif isinstance(db_config, dict):
                    db_url = db_config.get('url', 'sqlite:///modular_system.db')
                else:
                    db_url = 'sqlite:///modular_system.db'
                init_db(db_url)
                self.logger.log("base", f"Database initialized successfully: {db_url}", "info")
            else:
                init_db('sqlite:///modular_system.db')
                self.logger.log("base", "Database initialized with default settings", "info")
        except Exception as e:
            self.logger.log("base", f"Database initialization failed: {e}", "error")
            import traceback
            self.logger.log("base", f"Traceback: {traceback.format_exc()}", "error")
    def get_routes(self):
        from .routes import get_routes
        return get_routes(self)
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Core system functionality with database connections and monitoring',
            'author': 'Modular System Team',
            'dependencies': self._dependencies,
            'provides': ['database_connection', 'system_monitoring', 'health_checks', 'core_endpoints'],
            'endpoints': {
                '/': 'GET - Home page with module overview',
                '/health': 'GET - Health check page',
                '/status': 'GET - System status page',
                '/api/health': 'GET - Health check API (JSON)',
                '/api/status': 'GET - System status API (JSON)'
            },
            'features': [
                'Database connection management',
                'System health monitoring',
                'Beautiful home page',
                'Health check endpoints',
                'System status API',
                'Module registry integration',
                'Error handling and logging'
            ]
        }
    def get_system_status(self) -> Dict[str, Any]:
        if self.services and 'system_service' in self.services:
            return self.services['system_service'].get_system_status()
        else:
            return {
                'error': 'System service not initialized',
                'timestamp': str(datetime.now())
            }
    def get_timestamp(self) -> datetime:
        return datetime.now()
    def get_uptime(self) -> str:
        if self.services and 'system_service' in self.services:
            return self.services['system_service']._get_uptime()
        else:
            return "Unknown"
    def cleanup(self):
        try:
            self.logger.log("base", "Base module cleanup completed", "info")
        except Exception as e:
            self.logger.log("base", f"Error during cleanup: {e}", "error")
__version__ = "1.0.0"
__author__ = "Modular System Team"
__description__ = "Core system functionality with database connections and monitoring"
