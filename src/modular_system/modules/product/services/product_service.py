from typing import List, Optional, Dict, Any
from ..models.product import ProductModel
class ProductService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_all(self, organization_id: Optional[int] = None, category_id: Optional[int] = None) -> List[ProductModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                query = "SELECT * FROM products WHERE 1=1"
                params = {}
                if organization_id:
                    query += " AND organization_id = :org_id"
                    params['org_id'] = organization_id
                if category_id:
                    query += " AND category_id = :cat_id"
                    params['cat_id'] = category_id
                query += " ORDER BY name"
                result = conn.execute(text(query), params)
                items = [ProductModel.from_db_row(row) for row in result.fetchall()]
            self.logger.log("product", f"Retrieved {len(items)} items", "info")
            return items
        except Exception as e:
            self.logger.log("product", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[ProductModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM products WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = ProductModel.from_db_row(row)
                    self.logger.log("product", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("product", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: ProductModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("product", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO products (organization_id, name, description, price, stock, is_active)
                    VALUES (:organization_id, :name, :description, :price, :stock, :is_active)
                """), {
                    'organization_id': item.organization_id,
                    'name': item.name,
                    'description': item.description,
                    'price': item.price,
                    'stock': item.stock,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("product", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("product", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: ProductModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("product", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE products 
                    SET organization_id = :organization_id, name = :name, 
                        description = :description, price = :price, 
                        stock = :stock, is_active = :is_active,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    'id': item_id,
                    'organization_id': item.organization_id,
                    'name': item.name,
                    'description': item.description,
                    'price': item.price,
                    'stock': item.stock,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("product", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("product", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM products WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("product", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("product", f"Error deleting item: {e}", "error")
            return False
