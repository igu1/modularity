from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class WishlistModel(DatabaseModel):
    __tablename__ = 'wishlist_items'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if self.organization_id is None:
            errors.append("Organization ID is required")
        if self.user_id is None:
            errors.append("User ID is required")
        if self.product_id is None:
            errors.append("Product ID is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'user_id': self.user_id,
            'product_id': self.product_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WishlistModel':
        return cls(
            organization_id=data.get('organization_id'),
            user_id=data.get('user_id'),
            product_id=data.get('product_id')
        )
    @classmethod
    def from_db_row(cls, row) -> 'WishlistModel':
        return cls(
            id=row[0] if len(row) > 0 else None,
            organization_id=row[1] if len(row) > 1 else None,
            user_id=row[2] if len(row) > 2 else None,
            product_id=row[3] if len(row) > 3 else None,
            created_at=row[4] if len(row) > 4 else None,
            updated_at=row[5] if len(row) > 5 else None
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Wishlist(id={self.id}, name='{self.name}')>"
