from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class LoyaltyModel(DatabaseModel):
    __tablename__ = 'loyalty_points'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True, nullable=False)
    points = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if self.user_id is None:
            errors.append("User ID is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'points': self.points,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LoyaltyModel':
        return cls(
            user_id=data.get('user_id'),
            points=data.get('points', 0)
        )
    @classmethod
    def from_db_row(cls, row) -> 'LoyaltyModel':
        return cls(
            id=row[0],
            user_id=row[1],
            points=row[2],
            last_updated=row[3]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Loyalty(user_id={self.user_id}, points={self.points})>"
