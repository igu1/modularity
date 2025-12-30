from sqlalchemy import text
from modular_system.database.connection import get_engine
from ..models.cart import CartModel

class CartService:
    def __init__(self, module):
        self.module = module

    def get_all(self):
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, product_id, quantity FROM cart_items"))
            return [CartModel(id=row[0], product_id=row[1], quantity=row[2]) for row in result]

    def create(self, cart_item):
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(
                text("INSERT INTO cart_items (product_id, quantity) VALUES (:product_id, :quantity) RETURNING id"),
                {"product_id": cart_item.product_id, "quantity": cart_item.quantity}
            )
            cart_id = result.fetchone()[0]
            conn.commit()
            return cart_id
