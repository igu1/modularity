from typing import List, Optional, Dict, Any
from ..models.inventory import InventoryModel
class InventoryService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_low_stock_alerts(self) -> List[Dict[str, Any]]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                query = """
                    SELECT p.id, p.name, p.stock, t.min_stock 
                    FROM products p
                    JOIN inventory_thresholds t ON p.id = t.product_id
                    WHERE p.stock <= t.min_stock AND t.is_active = 1
                """
                result = conn.execute(text(query)).fetchall()
                return [dict(id=r[0], name=r[1], stock=r[2], threshold=r[3]) for r in result]
        except Exception as e:
            self.logger.log("inventory", f"Error getting alerts: {e}", "error")
            return []

    def set_threshold(self, product_id: int, min_stock: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO inventory_thresholds (product_id, min_stock) 
                    VALUES (:pid, :min)
                    ON CONFLICT(product_id) DO UPDATE SET min_stock = :min
                """), {"pid": product_id, "min": min_stock})
                conn.commit()
            return True
        except Exception as e:
            self.logger.log("inventory", f"Error setting threshold: {e}", "error")
            return False

    def get_all(self) -> List[InventoryModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM inventory_thresholds"))
                items = [InventoryModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("inventory", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[InventoryModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM inventorys WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = InventoryModel.from_db_row(row)
                    self.logger.log("inventory", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("inventory", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: InventoryModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("inventory", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO inventorys (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("inventory", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("inventory", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: InventoryModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("inventory", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE inventorys 
                    SET name = :name, description = :description, is_active = :is_active,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    'id': item_id,
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("inventory", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("inventory", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM inventorys WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("inventory", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("inventory", f"Error deleting item: {e}", "error")
            return False
