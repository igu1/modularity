from typing import List, Optional, Dict, Any
from ..models.subscription import SubscriptionModel
class SubscriptionService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_user_subscriptions(self, user_id: int) -> List[SubscriptionModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM subscriptions WHERE user_id = :uid"), {"uid": user_id}).fetchall()
                return [SubscriptionModel.from_db_row(row) for row in result]
        except Exception as e:
            self.logger.log("subscription", f"Error getting subscriptions: {e}", "error")
            return []

    def create_subscription(self, user_id: int, plan_name: str, price: float, period: str = 'monthly') -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO subscriptions (user_id, plan_name, price_per_period, billing_period, next_billing_date)
                    VALUES (:uid, :plan, :price, :period, datetime('now', '+1 month'))
                """), {
                    "uid": user_id,
                    "plan": plan_name,
                    "price": price,
                    "period": period
                })
                conn.commit()
            return True
        except Exception as e:
            self.logger.log("subscription", f"Error creating subscription: {e}", "error")
            return False

    def get_all(self) -> List[SubscriptionModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM subscriptions"))
                items = [SubscriptionModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("subscription", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[SubscriptionModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM subscriptions WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = SubscriptionModel.from_db_row(row)
                    self.logger.log("subscription", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("subscription", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: SubscriptionModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("subscription", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO subscriptions (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("subscription", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("subscription", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: SubscriptionModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("subscription", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE subscriptions 
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
                self.logger.log("subscription", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("subscription", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM subscriptions WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("subscription", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("subscription", f"Error deleting item: {e}", "error")
            return False
