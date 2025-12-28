from typing import List, Optional, Dict, Any
from ..models.checkout import CheckoutModel
class CheckoutService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def create_session(self, organization_id: int, user_id: int, cart_id: Optional[int] = None) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO checkout_sessions (organization_id, user_id, cart_id, status)
                    VALUES (:organization_id, :user_id, :cart_id, 'open')
                """), {
                    'organization_id': organization_id,
                    'user_id': user_id,
                    'cart_id': cart_id
                })
                conn.commit()
                session_id = result.lastrowid
                self.logger.log("checkout", f"Created checkout session ID: {session_id}", "info")
                return session_id
        except Exception as e:
            self.logger.log("checkout", f"Error creating checkout session: {e}", "error")
            return None
    def complete_checkout(self, session_id: int, shipping_address: str) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                session_result = conn.execute(text("SELECT * FROM checkout_sessions WHERE id = :id"), {'id': session_id})
                session_row = session_result.fetchone()
                if not session_row:
                    return False
                org_id = session_row[1]
                user_id = session_row[2]
                cart_id = session_row[3]
                cart_service = self.module.env.get_service('cart_service')
                cart_items = cart_service.get_user_cart(org_id, user_id)
                if not cart_items:
                    return False
                total_amount = 0
                order_items_data = []
                product_service = self.module.env.get_service('product_service')
                for item in cart_items:
                    product = product_service.get_by_id(item.product_id)
                    if product:
                        total_amount += product.price * item.quantity
                        order_items_data.append({
                            'product_id': item.product_id,
                            'quantity': item.quantity,
                            'price': product.price
                        })
                order_service = self.module.env.get_service('order_service')
                from ...modules.order.models.order import OrderModel
                new_order = OrderModel(
                    organization_id=org_id,
                    user_id=user_id,
                    total_amount=total_amount,
                    status='pending',
                    shipping_address=shipping_address
                )
                order_id = order_service.create(new_order, order_items_data)
                if order_id:
                    conn.execute(text("UPDATE checkout_sessions SET status = 'completed' WHERE id = :id"), {'id': session_id})
                    for item in cart_items:
                        cart_service.delete(item.id)
                    conn.commit()
                    return True
            return False
        except Exception as e:
            self.logger.log("checkout", f"Error completing checkout: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM checkouts WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("checkout", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("checkout", f"Error deleting item: {e}", "error")
            return False
