from typing import Dict, Any
from sqlalchemy import Column, Integer, ForeignKey, String
from modular_system.database.models import DatabaseModel

class CartModel(DatabaseModel):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, default=1)

    def to_dict(self) -> Dict[str, Any]:
        return {'id': self.id, 'user_id': self.user_id, 'product_id': self.product_id, 'quantity': self.quantity}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CartModel':
        return cls(
            user_id=data.get('user_id'),
            product_id=data.get('product_id'),
            quantity=data.get('quantity', 1)
        )
