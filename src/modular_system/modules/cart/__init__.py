from typing import Dict, Any, List
from modular_system.logging.logger import CoreLogger

class CartModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = 'cart'
        self.version = '1.0.0'
        self._dependencies = ['base', 'product']
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
        from .services.cart_service import CartService
        self.api_views = APIViews(self)
        self.services = {'cart_service': CartService(self)}
        if hasattr(env, 'register_service'):
            for k, v in self.services.items(): env.register_service(k, v)

    def _create_table(self):
        from modular_system.database.connection import get_engine
        from sqlalchemy import text
        engine = get_engine()
        sql = """
        CREATE TABLE IF NOT EXISTS cart_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id),
            product_id INTEGER NOT NULL, FOREIGN KEY (product_id) REFERENCES products(id),
            quantity INTEGER DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
        """
        with engine.connect() as conn:
            conn.execute(text(sql))
            conn.commit()

    def load_routes(self):
        from .routes import get_routes
        return get_routes(self)

    def get_info(self) -> Dict[str, Any]:
        return {'name': self.name, 'version': self.version, 'dependencies': self._dependencies}
