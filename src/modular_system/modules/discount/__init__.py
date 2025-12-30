from typing import Dict, Any, List, Optional
class DiscountModule:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.name = 'discount'
        self.version = '1.0.0'
        self._dependencies = ['base']
        self.env = None
        from modular_system.logging.logger import CoreLogger
        self.logger = CoreLogger()
        self.api_views = None
        self.services = None
        self.logger.log("discount", "discount module initialized", "info")
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    def initialize(self, env):
        self.env = env
        self._create_table()
        from .models.discount import DiscountModel, CouponModel
        # Make models available as attributes to avoid scope issues during registration
        self.DiscountModel = DiscountModel
        self.CouponModel = CouponModel
        from .services import DiscountService
        from .views import APIViews
        self.api_views = APIViews(self)
        self.services = {'discount_service': DiscountService(self)}
        if hasattr(env, 'register_service'):
            for k, v in self.services.items(): env.register_service(k, v)
        self.logger.log("discount", "discount module initialized with environment", "info")
    def _create_table(self):
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            
            statements = [
                """
                CREATE TABLE IF NOT EXISTS discounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """,
                """
                CREATE TABLE IF NOT EXISTS coupons (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code VARCHAR(50) UNIQUE NOT NULL,
                    discount_type VARCHAR(20) NOT NULL,
                    discount_value DECIMAL(10, 2) NOT NULL,
                    min_purchase DECIMAL(10, 2) DEFAULT 0,
                    expires_at DATETIME,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            ]
            
            with engine.connect() as conn:
                for statement in statements:
                    conn.execute(text(statement))
                conn.commit()
            self.logger.log("discount", "Created tables: discounts, coupons", "info")
        except Exception as e:
            self.logger.log("discount", f"Error creating table: {e}", "error")
    def load_routes(self):
        from .routes import get_routes
        return get_routes(self)
    def get_info(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'version': self.version,
            'description': 'Discount and coupon management system',
            'author': 'Modular System Team',
            'dependencies': self._dependencies,
            'provides': ['discount_feature1', 'discount_feature2'],
            'endpoints': {
                '/web/discount': 'GET - Main discount page',
                '/api/discount': 'GET - List coupons',
                '/api/discount/validate': 'POST - Validate coupon code'
            },
            'features': [
                'Feature 1',
                'Feature 2',
                'Feature 3'
            ]
        }
    def cleanup(self):
        try:
            self.logger.log("discount", "discount module cleanup completed", "info")
        except Exception as e:
            self.logger.log("discount", f"Error during cleanup: {e}", "error")
__version__ = "1.0.0"
__author__ = "Modular System Team"
__description__ = "Discount and coupon management system"
