from typing import Dict, Any, List, Optional
class LoyaltyModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = 'loyalty'
        self.version = '1.0.0'
        self._dependencies = ['base']
        self.env = None
        from modular_system.logging.logger import CoreLogger
        self.logger = CoreLogger()
        self.api_views = None
        self.services = None
        self.logger.log("loyalty", "loyalty module initialized", "info")
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    def initialize(self, env):
        self.env = env
        self._create_table()
        from .services import LoyaltyService
        from .views import APIViews
        self.api_views = APIViews(self)
        self.services = {'loyalty_service': LoyaltyService(self)}
        if hasattr(env, 'register_service'):
            for k, v in self.services.items(): env.register_service(k, v)
        self.logger.log("loyalty", "loyalty module initialized with environment", "info")
    def _create_table(self):
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS loyalty_points (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id),
                        points INTEGER DEFAULT 0,
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS loyalty_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id),
                        points_change INTEGER NOT NULL,
                        reason VARCHAR(255),
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
            self.logger.log("loyalty", f"Created tables: loyalty_points, loyalty_history", "info")
        except Exception as e:
            self.logger.log("loyalty", f"Error creating tables: {e}", "error")
    def load_routes(self):
        from .routes import get_routes
        return get_routes(self)
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Customer loyalty and points system',
            'author': 'Modular System Team',
            'dependencies': self._dependencies,
            'provides': ['loyalty_feature1', 'loyalty_feature2'],
            'endpoints': {
                '/web/loyalty': 'GET - Main loyalty page',
                '/api/loyalty/points/<user_id>': 'GET - User loyalty points',
                '/api/loyalty/add': 'POST - Add loyalty points'
            },
            'features': [
                'Feature 1',
                'Feature 2',
                'Feature 3'
            ]
        }
    def cleanup(self):
        try:
            self.logger.log("loyalty", "loyalty module cleanup completed", "info")
        except Exception as e:
            self.logger.log("loyalty", f"Error during cleanup: {e}", "error")
__version__ = "1.0.0"
__author__ = "Modular System Team"
__description__ = "Customer loyalty and points system"
