from typing import List, Optional, Dict, Any
from ..models.analytics import AnalyticsModel
class AnalyticsService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def track_event(self, event_type: str, user_id: int = None, path: str = None, metadata: dict = None) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            import json
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO analytics_events (event_type, user_id, path, metadata_json)
                    VALUES (:type, :uid, :path, :meta)
                """), {
                    "type": event_type,
                    "uid": user_id,
                    "path": path,
                    "meta": json.dumps(metadata or {})
                })
                conn.commit()
            return True
        except Exception as e:
            self.logger.log("analytics", f"Error tracking event: {e}", "error")
            return False

    def get_stats(self) -> Dict[str, int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT event_type, COUNT(*) as count 
                    FROM analytics_events 
                    GROUP BY event_type
                """)).fetchall()
                return {r[0]: r[1] for r in result}
        except Exception as e:
            self.logger.log("analytics", f"Error getting stats: {e}", "error")
            return {}

    def get_all(self) -> List[AnalyticsModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM analytics_events"))
                items = [AnalyticsModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("analytics", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[AnalyticsModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM analyticss WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = AnalyticsModel.from_db_row(row)
                    self.logger.log("analytics", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("analytics", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: AnalyticsModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("analytics", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO analyticss (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("analytics", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("analytics", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: AnalyticsModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("analytics", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE analyticss 
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
                self.logger.log("analytics", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("analytics", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM analyticss WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("analytics", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("analytics", f"Error deleting item: {e}", "error")
            return False
