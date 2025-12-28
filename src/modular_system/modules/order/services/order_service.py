from typing import List, Optional, Dict, Any
from ..models.order import OrderModel
class OrderService:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_all(self, organization_id: Optional[int] = None) -> List[OrderModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                query = "SELECT * FROM orders"
                params = {}
                if organization_id:
                    query += " WHERE organization_id = :org_id"
                    params['org_id'] = organization_id
                query += " ORDER BY created_at DESC"
                result = conn.execute(text(query), params)
                items = [OrderModel.from_db_row(row) for row in result.fetchall()]
            self.logger.log("order", f"Retrieved {len(items)} items", "info")
            return items
        except Exception as e:
            self.logger.log("order", f"Error getting all items: {e}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[OrderModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM orders WHERE id = :id"), {'id': item_id})
                row = result.fetchone()
                if row:
                    item = OrderModel.from_db_row(row)
                    self.logger.log("order", f"Retrieved item by ID: {item_id}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("order", f"Error getting item by ID: {e}", "error")
            return None
    def get_user_orders(self, organization_id: int, user_id: int) -> List[OrderModel]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM orders WHERE organization_id = :org_id AND user_id = :user_id ORDER BY created_at DESC"),
                                   {'org_id': organization_id, 'user_id': user_id})
                items = [OrderModel.from_db_row(row) for row in result.fetchall()]
            return items
        except Exception as e:
            self.logger.log("order", f"Error getting user orders: {e}", "error")
            return []
    def create(self, item: OrderModel, items: List[Dict[str, Any]]) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("order", f"Validation errors: {errors}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO orders (organization_id, user_id, total_amount, status, shipping_address)
                    VALUES (:organization_id, :user_id, :total_amount, :status, :shipping_address)
                """), {
                    'organization_id': item.organization_id,
                    'user_id': item.user_id,
                    'total_amount': item.total_amount,
                    'status': item.status,
                    'shipping_address': item.shipping_address
                })
                order_id = result.lastrowid
                for order_item in items:
                    conn.execute(text("""
                        INSERT INTO order_items (order_id, product_id, quantity, price)
                        VALUES (:order_id, :product_id, :quantity, :price)
                    """), {
                        'order_id': order_id,
                        'product_id': order_item['product_id'],
                        'quantity': order_item['quantity'],
                        'price': order_item['price']
                    })
                conn.commit()
                self.logger.log("order", f"Created order ID: {order_id}", "info")
                return order_id
        except Exception as e:
            self.logger.log("order", f"Error creating order: {e}", "error")
            return None
    def update_status(self, order_id: int, status: str) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text("UPDATE orders SET status = :status, updated_at = CURRENT_TIMESTAMP WHERE id = :id"),
                           {'id': order_id, 'status': status})
                conn.commit()
                return True
        except Exception as e:
            self.logger.log("order", f"Error updating order status: {e}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM orders WHERE id = :id"), {'id': item_id})
                conn.commit()
                self.logger.log("order", f"Deleted item ID: {item_id}", "info")
                return True
        except Exception as e:
            self.logger.log("order", f"Error deleting item: {e}", "error")
            return False
