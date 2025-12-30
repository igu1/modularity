from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class RecommendationModel(DatabaseModel):
    __tablename__ = 'product_recommendations'
    product_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    recommended_id = Column(Integer, ForeignKey('products.id'), primary_key=True)
    rec_type = Column(String(20), default='related') # related, upsell, cross_sell
    score = Column(Integer, default=0)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if self.product_id is None or self.recommended_id is None:
            errors.append("Product ID and Recommended ID are required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'product_id': self.product_id,
            'recommended_id': self.recommended_id,
            'type': self.rec_type,
            'score': self.score
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecommendationModel':
        return cls(
            product_id=data.get('product_id'),
            recommended_id=data.get('recommended_id'),
            rec_type=data.get('rec_type', 'related'),
            score=data.get('score', 0)
        )
    @classmethod
    def from_db_row(cls, row) -> 'RecommendationModel':
        return cls(
            product_id=row[0],
            recommended_id=row[1],
            rec_type=row[2],
            score=row[3]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Recommendation(pid={self.product_id}, rid={self.recommended_id}, type='{self.rec_type}')>"
