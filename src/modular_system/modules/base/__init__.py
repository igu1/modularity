from typing import Dict, Any, List
from datetime import datetime
from modular_system.database.connection import init_db, get_engine
from sqlalchemy import text

class BaseModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config, self.name, self.version = config or {}, 'base', '1.0.0'
        db_url = self.config.get('database', {}).get('url', 'sqlite:///modular_system.db') if isinstance(self.config, dict) else 'sqlite:///modular_system.db'
        init_db(db_url)

    @property
    def dependencies(self) -> List[str]: return []

    def initialize(self, env):
        self.env = env
        try:
            with get_engine().connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS organizations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name VARCHAR(255) NOT NULL,
                        slug VARCHAR(100) UNIQUE NOT NULL,
                        domain VARCHAR(255) UNIQUE,
                        description TEXT,
                        is_active BOOLEAN DEFAULT 1,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
        except: pass
        
        from .services import SystemService, OrganizationService
        self.services = {'system_service': SystemService(self), 'organization_service': OrganizationService(self)}
        if hasattr(env, 'register_service'):
            for k, v in self.services.items(): env.register_service(k, v)

    def load_routes(self):
        from .routes import get_routes
        return get_routes(self)

    def get_info(self) -> Dict[str, Any]:
        return {'name': self.name, 'version': self.version, 'dependencies': []}

    def get_system_status(self) -> Dict[str, Any]:
        return self.services['system_service'].get_system_status() if 'system_service' in self.services else {'ts': str(datetime.now())}

    def cleanup(self): pass
__version__ = "1.0.0"
__author__ = "Modular System Team"
__description__ = "Core system functionality with database connections and monitoring"
