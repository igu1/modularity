from typing import Dict, Any, List, Optional
class SupportModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = 'support'
        self.version = '1.0.0'
        self._dependencies = ['base']
        self.env = None
        from modular_system.logging.logger import CoreLogger
        self.logger = CoreLogger()
        self.api_views = None
        self.services = None
        self.logger.log("support", "support module initialized", "info")
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    def initialize(self, env):
        self.env = env
        self._create_table()
        from .services import SupportService
        from .views import APIViews
        self.api_views = APIViews(self)
        self.services = {'support_service': SupportService(self)}
        if hasattr(env, 'register_service'):
            for k, v in self.services.items(): env.register_service(k, v)
        self.logger.log("support", "support module initialized with environment", "info")
    def _create_table(self):
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS support_tickets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        subject VARCHAR(255) NOT NULL,
                        status VARCHAR(20) DEFAULT 'open',
                        priority VARCHAR(20) DEFAULT 'medium',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """))
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS ticket_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ticket_id INTEGER NOT NULL,
                        sender_id INTEGER NOT NULL,
                        message TEXT NOT NULL,
                        is_admin BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (ticket_id) REFERENCES support_tickets(id),
                        FOREIGN KEY (sender_id) REFERENCES users(id)
                    )
                """))
                conn.commit()
            self.logger.log("support", f"Created tables: support_tickets, ticket_messages", "info")
        except Exception as e:
            self.logger.log("support", f"Error creating tables: {e}", "error")
    def load_routes(self):
        from .routes import get_routes
        return get_routes(self)
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Customer support ticketing system',
            'author': 'Modular System Team',
            'dependencies': self._dependencies,
            'provides': ['support_feature1', 'support_feature2'],
            'endpoints': {
                '/web/support': 'GET - Main support page',
                '/api/support/tickets/<user_id>': 'GET - User support tickets',
                '/api/support/tickets/create': 'POST - Create support ticket'
            },
            'features': [
                'Feature 1',
                'Feature 2',
                'Feature 3'
            ]
        }
    def cleanup(self):
        try:
            self.logger.log("support", "support module cleanup completed", "info")
        except Exception as e:
            self.logger.log("support", f"Error during cleanup: {e}", "error")
__version__ = "1.0.0"
__author__ = "Modular System Team"
__description__ = "Customer support ticketing system"
