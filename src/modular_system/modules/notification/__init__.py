from typing import Dict, Any, List, Optional
class NotificationModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = 'notification'
        self.version = '1.0.0'
        self._dependencies = ['base']
        self.env = None
        from modular_system.logging.logger import CoreLogger
        self.logger = CoreLogger()
        self.api_views = None
        self.services = None
        self.logger.log("notification", "notification module initialized", "info")
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    def initialize(self, env):
        self.env = env
        self._create_table()
        from .services import NotificationService
        from .views import APIViews
        self.api_views = APIViews(self)
        self.services = {'notification_service': NotificationService(self)}
        if hasattr(env, 'register_service'):
            for k, v in self.services.items(): env.register_service(k, v)
        self.logger.log("notification", "notification module initialized with environment", "info")
    def _create_table(self):
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id),
                        title VARCHAR(255) NOT NULL,
                        message TEXT,
                        type VARCHAR(50) DEFAULT 'info',
                        is_read BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
            self.logger.log("notification", f"Created table: notifications", "info")
        except Exception as e:
            self.logger.log("notification", f"Error creating table: {e}", "error")
    def load_routes(self):
        from .routes import get_routes
        return get_routes(self)
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': 'In-app notification system',
            'author': 'Modular System Team',
            'dependencies': self._dependencies,
            'provides': ['notification_feature1', 'notification_feature2'],
            'endpoints': {
                '/web/notification': 'GET - Main notification page',
                '/api/notifications/<user_id>': 'GET - User notifications',
                '/api/notifications/read': 'POST - Mark as read'
            },
            'features': [
                'Feature 1',
                'Feature 2',
                'Feature 3'
            ]
        }
    def cleanup(self):
        try:
            self.logger.log("notification", "notification module cleanup completed", "info")
        except Exception as e:
            self.logger.log("notification", f"Error during cleanup: {e}", "error")
__version__ = "1.0.0"
__author__ = "Modular System Team"
__description__ = "In-app notification system"
