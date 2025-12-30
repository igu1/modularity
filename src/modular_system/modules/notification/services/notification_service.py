from typing import List, Optional, Dict, Any
from ..models.notification import NotificationModel
class NotificationService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_user_notifications(self, user_id: int) -> List[NotificationModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT * FROM notifications 
                    WHERE user_id = :uid 
                    ORDER BY created_at DESC
                """), {"uid": user_id}).fetchall()
                return [NotificationModel.from_db_row(row) for row in result]
        except Exception as e:
            self.logger.log("notification", f"Error getting notifications: {e}", "error")
            return []

    def mark_as_read(self, notification_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("UPDATE notifications SET is_read = 1 WHERE id = :id"), {"id": notification_id})
                conn.commit()
            return True
        except Exception as e:
            self.logger.log("notification", f"Error marking as read: {e}", "error")
            return False

    def get_all(self) -> List[NotificationModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM notifications"))
                items = [NotificationModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("notification", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[NotificationModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM notifications WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = NotificationModel.from_db_row(row)
                    self.logger.log("notification", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("notification", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: NotificationModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("notification", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO notifications (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("notification", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("notification", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: NotificationModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("notification", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE notifications 
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
                self.logger.log("notification", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("notification", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM notifications WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("notification", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("notification", f"Error deleting item: {e}", "error")
            return False
