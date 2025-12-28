from typing import Dict, Any, List, Optional
class OrderModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = 'order'
        self.version = '1.0.0'
        self._dependencies = ['base']
        self.env = None
        from modular_system.logging.logger import CoreLogger
        self.logger = CoreLogger()
        self.web_views = None
        self.api_views = None
        self.services = None
        self.logger.log("order", "order module initialized", "info")
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    def initialize(self, env):
        self.env = env
        self._create_table()
        from .views import WebViews, APIViews
        from .services import OrderService
        self.web_views = WebViews(self)
        self.api_views = APIViews(self)
        self.services = {'order_service': OrderService(self)}
        if hasattr(env, 'register_service'):
            env.register_service('order_service', self.services['order_service'])
        
        self.logger.log("order", "order module initialized with environment", "info")
    def load_routes(self):
        from .routes import get_routes
        return get_routes(self)
    def _create_table(self):
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                organization_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                total_amount INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'pending',
                shipping_address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations(id)
            )
            """
            create_order_items_table = f"""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER DEFAULT 1,
                price INTEGER NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
            """
            with engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.execute(text(create_order_items_table))
                conn.commit()
            self.logger.log("order", f"Created tables: orders, order_items", "info")
        except Exception as e:
            self.logger.log("order", f"Error creating table: {e}", "error")
    def get_routes(self):
        from .routes import get_routes
        return get_routes(self)
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Order management and tracking',
            'author': 'Modular System Team',
            'dependencies': self._dependencies,
            'provides': ['order_feature1', 'order_feature2'],
            'endpoints': {
                '/order': 'GET - Main order page',
                '/order/create': 'GET/POST - Create new item',
                '/order/<id>': 'GET - View item details',
                '/api/order': 'GET - API endpoint (JSON)'
            },
            'features': [
                'Feature 1',
                'Feature 2',
                'Feature 3'
            ]
        }
    def cleanup(self):
        try:
            self.logger.log("order", "order module cleanup completed", "info")
        except Exception as e:
            self.logger.log("order", f"Error during cleanup: {e}", "error")
__version__ = "1.0.0"
__author__ = "Modular System Team"
__description__ = "Order management and tracking"
