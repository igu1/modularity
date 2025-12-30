from typing import List, Optional, Dict, Any
from ..models.support import SupportModel
class SupportService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def create_ticket(self, user_id: int, subject: str, message: str, priority: str = 'medium') -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    INSERT INTO support_tickets (user_id, subject, priority)
                    VALUES (:uid, :subject, :priority)
                    RETURNING id
                """), {"uid": user_id, "subject": subject, "priority": priority})
                ticket_id = result.fetchone()[0]
                conn.execute(text("""
                    INSERT INTO ticket_messages (ticket_id, sender_id, message)
                    VALUES (:tid, :uid, :msg)
                """), {"tid": ticket_id, "uid": user_id, "msg": message})
                conn.commit()
                return ticket_id
        except Exception as e:
            self.logger.log("support", f"Error creating ticket: {e}", "error")
            return None

    def get_user_tickets(self, user_id: int) -> List[SupportModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM support_tickets WHERE user_id = :uid ORDER BY updated_at DESC"), {"uid": user_id}).fetchall()
                return [SupportModel.from_db_row(row) for row in result]
        except Exception as e:
            self.logger.log("support", f"Error getting tickets: {e}", "error")
            return []

    def get_all(self) -> List[SupportModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM support_tickets"))
                items = [SupportModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("support", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[SupportModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM supports WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = SupportModel.from_db_row(row)
                    self.logger.log("support", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("support", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: SupportModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("support", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO supports (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("support", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("support", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: SupportModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("support", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE supports 
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
                self.logger.log("support", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("support", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM supports WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("support", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("support", f"Error deleting item: {e}", "error")
            return False
