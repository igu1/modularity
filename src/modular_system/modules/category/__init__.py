from typing import Dict, Any, List
from modular_system.logging.logger import CoreLogger

class CategoryModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = 'category'
        self.version = '1.0.0'
        self._dependencies = ['base']
        self.logger = CoreLogger()
        self.api_views = None
        self.services = None

    @property
    def dependencies(self) -> List[str]:
        return self._dependencies

    def initialize(self, env):
        self.env = env
        self._create_table()
        from .views import APIViews
        from .services.category_service import CategoryService
        self.api_views = APIViews(self)
        self.services = {'category_service': CategoryService(self)}
        if hasattr(env, 'register_service'):
            for k, v in self.services.items(): env.register_service(k, v)

    def _create_table(self):
        from modular_system.database.connection import get_engine
        from sqlalchemy import text
        engine = get_engine()
        sql = "CREATE TABLE IF NOT EXISTS categories (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(255) NOT NULL)"
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()

    def load_routes(self):
        from .routes import get_routes
        return get_routes(self)

    def get_info(self) -> Dict[str, Any]:
        return {'name': self.name, 'version': self.version, 'dependencies': self._dependencies}
