from typing import List, Optional, Dict, Any
from ..models.product import ProductModel
class ProductService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_all(self) -> List[ProductModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM products ORDER BY name"))
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
                    INSERT INTO products (name, description, category_id, is_active)
                    VALUES (:name, :description, :category_id, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'category_id': item.category_id,
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
                    SET name = :name, description = :description, category_id = :category_id, is_active = :is_active,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    'id': item_id,
                    'name': item.name,
                    'description': item.description,
                    'category_id': item.category_id,
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
