from typing import List, Optional, Dict, Any
from ..models.review import ReviewModel
class ReviewService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_product_reviews(self, product_id: int) -> Dict[str, Any]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM product_reviews WHERE product_id = :id ORDER BY created_at DESC"), {"id": product_id}).fetchall()
                reviews = [ReviewModel.from_db_row(row) for row in result]
                avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
                return {
                    "product_id": product_id,
                    "average_rating": avg_rating,
                    "reviews": reviews
                }
        except Exception as e:
            self.logger.log("review", f"Error getting reviews: {e}", "error")
            return {"product_id": product_id, "average_rating": 0, "reviews": []}

    def submit_review(self, review: ReviewModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO product_reviews (product_id, user_id, rating, comment, is_verified_purchase)
                    VALUES (:pid, :uid, :rating, :comment, :verified)
                """), {
                    "pid": review.product_id,
                    "uid": review.user_id,
                    "rating": review.rating,
                    "comment": review.comment,
                    "verified": review.is_verified_purchase
                })
                conn.commit()
            return True
        except Exception as e:
            self.logger.log("review", f"Error submitting review: {e}", "error")
            return False

    def get_all(self) -> List[ReviewModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM product_reviews"))
                items = [ReviewModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("review", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[ReviewModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM reviews WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = ReviewModel.from_db_row(row)
                    self.logger.log("review", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("review", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: ReviewModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("review", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO reviews (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("review", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("review", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: ReviewModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("review", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE reviews 
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
                self.logger.log("review", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("review", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM reviews WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("review", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("review", f"Error deleting item: {e}", "error")
            return False
