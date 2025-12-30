from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class WishlistModel(DatabaseModel):
    __tablename__ = 'wishlists'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if self.user_id is None or self.product_id is None:
            errors.append("User ID and Product ID are required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WishlistModel':
        return cls(
            user_id=data.get('user_id'),
            product_id=data.get('product_id')
        )
    @classmethod
    def from_db_row(cls, row) -> 'WishlistModel':
        return cls(
            id=row[0],
            user_id=row[1],
            product_id=row[2],
            created_at=row[3]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Wishlist(user={self.user_id}, product={self.product_id})>"
