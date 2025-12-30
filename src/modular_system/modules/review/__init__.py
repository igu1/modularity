from typing import Dict, Any, List, Optional
class ReviewModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = 'review'
        self.version = '1.0.0'
        self._dependencies = ['base']
        self.env = None
        from modular_system.logging.logger import CoreLogger
        self.logger = CoreLogger()
        self.api_views = None
        self.services = None
        self.logger.log("review", "review module initialized", "info")
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    def initialize(self, env):
        self.env = env
        self._create_table()
        from .services import ReviewService
        from .views import APIViews
        self.api_views = APIViews(self)
        self.services = {'review_service': ReviewService(self)}
        if hasattr(env, 'register_service'):
            for k, v in self.services.items(): env.register_service(k, v)
        self.logger.log("review", "review module initialized with environment", "info")
    def _create_table(self):
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS product_reviews (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_id INTEGER NOT NULL, FOREIGN KEY (product_id) REFERENCES products(id),
                        user_id INTEGER NOT NULL, FOREIGN KEY (user_id) REFERENCES users(id),
                        rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                        comment TEXT,
                        is_verified_purchase BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """))
                conn.commit()
            self.logger.log("review", f"Created table: product_reviews", "info")
        except Exception as e:
            self.logger.log("review", f"Error creating table: {e}", "error")
    def load_routes(self):
        from .routes import get_routes
        return get_routes(self)
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Product reviews and ratings',
            'author': 'Modular System Team',
            'dependencies': self._dependencies,
            'provides': ['review_feature1', 'review_feature2'],
            'endpoints': {
                '/web/review': 'GET - Main review page',
                '/api/product/<id>/reviews': 'GET - Product reviews',
                '/api/review/submit': 'POST - Submit product review'
            },
            'features': [
                'Feature 1',
                'Feature 2',
                'Feature 3'
            ]
        }
    def cleanup(self):
        try:
            self.logger.log("review", "review module cleanup completed", "info")
        except Exception as e:
            self.logger.log("review", f"Error during cleanup: {e}", "error")
__version__ = "1.0.0"
__author__ = "Modular System Team"
__description__ = "Product reviews and ratings"
