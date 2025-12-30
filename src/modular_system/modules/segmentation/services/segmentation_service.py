from typing import List, Optional, Dict, Any
from ..models.segmentation import SegmentModel, SegmentationModel
class SegmentationService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def assign_to_segment(self, user_id: int, segment_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT OR IGNORE INTO user_segments (user_id, segment_id) 
                    VALUES (:uid, :sid)
                """), {"uid": user_id, "sid": segment_id})
                conn.commit()
            return True
        except Exception as e:
            self.logger.log("segmentation", f"Error assigning segment: {e}", "error")
            return False

    def get_user_segments(self, user_id: int) -> List[SegmentModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT s.* FROM segments s
                    JOIN user_segments us ON s.id = us.segment_id
                    WHERE us.user_id = :uid
                """), {"uid": user_id}).fetchall()
                return [SegmentModel.from_db_row(row) for row in result]
        except Exception as e:
            self.logger.log("segmentation", f"Error getting user segments: {e}", "error")
            return []

    def get_all(self) -> List[SegmentModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM segments"))
                items = [SegmentModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("segmentation", f"Error getting all segments: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[SegmentationModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM segmentations WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = SegmentationModel.from_db_row(row)
                    self.logger.log("segmentation", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("segmentation", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: SegmentationModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("segmentation", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO segmentations (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("segmentation", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("segmentation", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: SegmentationModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("segmentation", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE segmentations 
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
                self.logger.log("segmentation", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("segmentation", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM segmentations WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("segmentation", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("segmentation", f"Error deleting item: {e}", "error")
            return False
