from typing import List, Optional, Dict, Any
from ..models.recommendation import RecommendationModel
class RecommendationService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_recommendations(self, product_id: int) -> List[Dict[str, Any]]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                query = """
                    SELECT p.*, r.rec_type, r.score 
                    FROM products p
                    JOIN product_recommendations r ON p.id = r.recommended_id
                    WHERE r.product_id = :pid
                    ORDER BY r.score DESC
                """
                result = conn.execute(text(query), {"pid": product_id}).fetchall()
                return [dict(id=r[0], name=r[1], price=float(r[3]) if r[3] else 0, type=r[4], score=r[5]) for r in result]
        except Exception as e:
            self.logger.log("recommendation", f"Error getting recommendations: {e}", "error")
            return []

    def add_recommendation(self, product_id: int, recommended_id: int, rec_type: str = 'related', score: int = 0) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT OR REPLACE INTO product_recommendations (product_id, recommended_id, rec_type, score)
                    VALUES (:pid, :rid, :type, :score)
                """), {
                    "pid": product_id,
                    "rid": recommended_id,
                    "type": rec_type,
                    "score": score
                })
                conn.commit()
            return True
        except Exception as e:
            self.logger.log("recommendation", f"Error adding recommendation: {e}", "error")
            return False

    def get_all(self) -> List[RecommendationModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM product_recommendations"))
                items = [RecommendationModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("recommendation", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[RecommendationModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM recommendations WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = RecommendationModel.from_db_row(row)
                    self.logger.log("recommendation", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("recommendation", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: RecommendationModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("recommendation", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO recommendations (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("recommendation", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("recommendation", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: RecommendationModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("recommendation", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE recommendations 
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
                self.logger.log("recommendation", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("recommendation", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM recommendations WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("recommendation", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("recommendation", f"Error deleting item: {e}", "error")
            return False
