from typing import Dict, Any, List, Optional
class ProductModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = 'product'
        self.version = '1.0.0'
        self._dependencies = ['base']
        self.env = None
        from modular_system.logging.logger import CoreLogger
        self.logger = CoreLogger()
        self.web_views = None
        self.api_views = None
        self.services = None
        self.logger.log("product", "product module initialized", "info")
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    def initialize(self, env):
        self.env = env
        self._create_table()
        from .views import WebViews, APIViews
        from .services import ProductService
        self.web_views = WebViews(self)
        self.api_views = APIViews(self)
        self.services = {'product_service': ProductService(self)}
        if hasattr(env, 'register_service'):
            for k, v in self.services.items(): env.register_service(k, v)
        self.logger.log("product", "product module initialized with environment", "info")
    def _create_table(self):
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            with engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
            self.logger.log("product", f"Created table: products", "info")
        except Exception as e:
            self.logger.log("product", f"Error creating table: {e}", "error")
    def load_routes(self):
        from .routes import get_routes
        return get_routes(self)
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Product management module',
            'author': 'Modular System Team',
            'dependencies': self._dependencies,
            'provides': ['product_feature1', 'product_feature2'],
            'endpoints': {
                '/product': 'GET - Main product page',
                '/product/create': 'GET/POST - Create new item',
                '/product/<id>': 'GET - View item details',
                '/api/product': 'GET - API endpoint (JSON)'
            },
            'features': [
                'Feature 1',
                'Feature 2',
                'Feature 3'
            ]
        }
    def cleanup(self):
        try:
            self.logger.log("product", "product module cleanup completed", "info")
        except Exception as e:
            self.logger.log("product", f"Error during cleanup: {e}", "error")
__version__ = "1.0.0"
__author__ = "Modular System Team"
__description__ = "Product management module"
