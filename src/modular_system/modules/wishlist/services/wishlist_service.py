from typing import List, Optional, Dict, Any
from ..models.wishlist import WishlistModel
class WishlistService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_user_wishlist(self, organization_id: int, user_id: int) -> List[WishlistModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM wishlist_items WHERE organization_id = :org_id AND user_id = :user_id"), 
                                   {'org_id': organization_id, 'user_id': user_id})
                items = [WishlistModel.from_db_row(row) for row in result.fetchall()]
            self.logger.log("wishlist", f"Retrieved {len(items)} items for user {user_id}", "info")
            return items
        except Exception as e:
            self.logger.log("wishlist", f"Error getting user wishlist: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[WishlistModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM wishlist_items WHERE id = :id"), {'id': item_id})
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
                    INSERT INTO wishlist_items (organization_id, user_id, product_id)
                    VALUES (:organization_id, :user_id, :product_id)
                """), {
                    'organization_id': item.organization_id,
                    'user_id': item.user_id,
                    'product_id': item.product_id
                })
                conn.commit()
                self.logger.log("wishlist", f"Added to wishlist for user: {item.user_id}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("wishlist", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: WishlistModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE wishlist_items 
                    SET product_id = :product_id,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    'id': item_id,
                    'product_id': item.product_id
                })
                conn.commit()
                self.logger.log("wishlist", f"Updated wishlist item ID: {item_id}", "info")
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
                conn.execute(text(f"DELETE FROM wishlist_items WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("wishlist", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("wishlist", f"Error deleting item: {e}", "error")
            return False
