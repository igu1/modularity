from typing import List, Optional, Dict, Any
from ..models.shipping import ShippingModel
class ShippingService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_active_methods(self) -> List[ShippingModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM shipping_methods WHERE is_active = 1")).fetchall()
                return [ShippingModel.from_db_row(row) for row in result]
        except Exception as e:
            self.logger.log("shipping", f"Error getting methods: {e}", "error")
            return []

    def update_tracking(self, order_id: int, carrier: str, tracking: str, status: str = 'shipped') -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO shipment_tracking (order_id, carrier, tracking_number, status)
                    VALUES (:oid, :carrier, :tracking, :status)
                    ON CONFLICT(order_id) DO UPDATE SET 
                    status = :status, 
                    last_updated = CURRENT_TIMESTAMP
                """), {
                    "oid": order_id,
                    "carrier": carrier,
                    "tracking": tracking,
                    "status": status
                })
                conn.commit()
            return True
        except Exception as e:
            self.logger.log("shipping", f"Error updating tracking: {e}", "error")
            return False

    def get_all(self) -> List[ShippingModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM shipping_methods"))
                items = [ShippingModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("shipping", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[ShippingModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM shippings WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = ShippingModel.from_db_row(row)
                    self.logger.log("shipping", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("shipping", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: ShippingModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("shipping", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO shippings (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("shipping", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("shipping", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: ShippingModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("shipping", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE shippings 
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
                self.logger.log("shipping", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("shipping", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM shippings WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("shipping", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("shipping", f"Error deleting item: {e}", "error")
            return False
