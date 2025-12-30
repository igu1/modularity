from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class ShippingModel(DatabaseModel):
    __tablename__ = 'shipping_methods'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    base_cost = Column(Integer, nullable=False)
    estimated_days = Column(String(50))
    is_active = Column(Boolean, default=True)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.name:
            errors.append("Name is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'cost': self.base_cost,
            'days': self.estimated_days,
            'is_active': self.is_active
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShippingModel':
        return cls(
            name=data.get('name', ''),
            base_cost=data.get('cost', 0),
            estimated_days=data.get('days')
        )
    @classmethod
    def from_db_row(cls, row) -> 'ShippingModel':
        return cls(
            id=row[0],
            name=row[1],
            base_cost=row[2],
            estimated_days=row[3],
            is_active=row[4]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<ShippingMethod(id={self.id}, name='{self.name}', cost={self.base_cost})>"
