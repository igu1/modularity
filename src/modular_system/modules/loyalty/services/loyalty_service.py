from typing import List, Optional, Dict, Any
from ..models.loyalty import LoyaltyModel
class LoyaltyService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_points(self, user_id: int) -> int:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT points FROM loyalty_points WHERE user_id = :id"), {"id": user_id}).fetchone()
                return result[0] if result else 0
        except Exception as e:
            self.logger.log("loyalty", f"Error getting points: {e}", "error")
            return 0

    def add_points(self, user_id: int, points: int, reason: str = "Purchase") -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO loyalty_points (user_id, points) 
                    VALUES (:user_id, :points)
                    ON CONFLICT(user_id) DO UPDATE SET 
                    points = points + :points,
                    last_updated = CURRENT_TIMESTAMP
                """), {"user_id": user_id, "points": points})
                conn.execute(text("""
                    INSERT INTO loyalty_history (user_id, points_change, reason)
                    VALUES (:user_id, :points, :reason)
                """), {"user_id": user_id, "points": points, "reason": reason})
                conn.commit()
            return True
        except Exception as e:
            self.logger.log("loyalty", f"Error adding points: {e}", "error")
            return False

    def get_all(self) -> List[LoyaltyModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM loyalty_points"))
                items = [LoyaltyModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("loyalty", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[LoyaltyModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM loyaltys WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = LoyaltyModel.from_db_row(row)
                    self.logger.log("loyalty", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("loyalty", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: LoyaltyModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("loyalty", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO loyaltys (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("loyalty", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("loyalty", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: LoyaltyModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("loyalty", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE loyaltys 
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
                self.logger.log("loyalty", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("loyalty", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM loyaltys WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("loyalty", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("loyalty", f"Error deleting item: {e}", "error")
            return False
