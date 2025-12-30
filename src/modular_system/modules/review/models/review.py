from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class ReviewModel(DatabaseModel):
    __tablename__ = 'product_reviews'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Integer)
    comment = Column(Text)
    is_verified_purchase = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if self.rating and (self.rating < 1 or self.rating > 5):
            errors.append("Rating must be between 1 and 5")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'product_id': self.product_id,
            'user_id': self.user_id,
            'rating': self.rating,
            'comment': self.comment,
            'verified': self.is_verified_purchase,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReviewModel':
        return cls(
            product_id=data.get('product_id'),
            user_id=data.get('user_id'),
            rating=data.get('rating'),
            comment=data.get('comment'),
            is_verified_purchase=data.get('verified', False)
        )
    @classmethod
    def from_db_row(cls, row) -> 'ReviewModel':
        return cls(
            id=row[0],
            product_id=row[1],
            user_id=row[2],
            rating=row[3],
            comment=row[4],
            is_verified_purchase=row[5],
            created_at=row[6]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Review(product={self.product_id}, user={self.user_id}, rating={self.rating})>"
