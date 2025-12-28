from typing import List, Optional, Dict, Any
from ..models.cart import CartModel
class CartService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_user_cart(self, organization_id: int, user_id: int) -> List[CartModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM cart_items WHERE organization_id = :org_id AND user_id = :user_id"), 
                                   {'org_id': organization_id, 'user_id': user_id})
                items = [CartModel.from_db_row(row) for row in result.fetchall()]
            self.logger.log("cart", f"Retrieved {len(items)} items for user {user_id}", "info")
            return items
        except Exception as e:
            self.logger.log("cart", f"Error getting user cart: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[CartModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM cart_items WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = CartModel.from_db_row(row)
                    self.logger.log("cart", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("cart", f"Error getting item by ID: {e}", "error")
            return None
    def create(self, item: CartModel) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("cart", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO cart_items (organization_id, user_id, product_id, quantity)
                    VALUES (:organization_id, :user_id, :product_id, :quantity)
                """), {
                    'organization_id': item.organization_id,
                    'user_id': item.user_id,
                    'product_id': item.product_id,
                    'quantity': item.quantity
                })
                conn.commit()
                self.logger.log("cart", f"Created cart item for user: {item.user_id}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("cart", f"Error creating item: {e}", "error")
            return None
    def update(self, item_id: int, item: CartModel) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE cart_items 
                    SET quantity = :quantity,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {
                    'id': item_id,
                    'quantity': item.quantity
                })
                conn.commit()
                self.logger.log("cart", f"Updated cart item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("cart", f"Error updating item: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM cart_items WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("cart", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("cart", f"Error deleting item: {e}", "error")
            return False
