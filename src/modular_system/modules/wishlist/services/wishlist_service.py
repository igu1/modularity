from typing import List, Optional, Dict, Any
from ..models.wishlist import WishlistModel
class WishlistService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_user_wishlist(self, user_id: int) -> List[Dict[str, Any]]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                query = """
                    SELECT p.* FROM products p
                    JOIN wishlists w ON p.id = w.product_id
                    WHERE w.user_id = :uid
                """
                result = conn.execute(text(query), {"uid": user_id}).fetchall()
                return [dict(id=r[0], name=r[1], price=float(r[3]) if r[3] else 0) for r in result]
        except Exception as e:
            self.logger.log("wishlist", f"Error getting wishlist: {e}", "error")
            return []

    def add_to_wishlist(self, user_id: int, product_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT OR IGNORE INTO wishlists (user_id, product_id)
                    VALUES (:uid, :pid)
                """), {"uid": user_id, "pid": product_id})
                conn.commit()
            return True
        except Exception as e:
            self.logger.log("wishlist", f"Error adding to wishlist: {e}", "error")
            return False

    def get_all(self) -> List[WishlistModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM wishlists"))
                items = [WishlistModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("wishlist", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[WishlistModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM wishlists WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = WishlistModel.from_db_row(row)
                    self.logger.log("wishlist", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("wishlist", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: WishlistModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("wishlist", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO wishlists (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                })
                conn.commit()
                self.logger.log("wishlist", f"Created item: {item.name}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("wishlist", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: WishlistModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("wishlist", f"Validation errors: {errors}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE wishlists 
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
                self.logger.log("wishlist", f"Updated item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("wishlist", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM wishlists WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("wishlist", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("wishlist", f"Error deleting item: {e}", "error")
            return False
