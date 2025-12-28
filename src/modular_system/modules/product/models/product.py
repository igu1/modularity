from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class ProductModel(DatabaseModel):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Name is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if hasattr(self.created_at, 'isoformat') else self.created_at,
            'updated_at': self.updated_at.isoformat() if hasattr(self.updated_at, 'isoformat') else self.updated_at
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductModel':
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
    @classmethod
    def from_db_row(cls, row) -> 'ProductModel':
        return cls(
            id=row[0] if len(row) > 0 else None,
            name=row[1] if len(row) > 1 else '',
            description=row[2] if len(row) > 2 else '',
            is_active=row[3] if len(row) > 3 else True,
            created_at=row[4] if len(row) > 4 else None,
            updated_at=row[5] if len(row) > 5 else None
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}')>"
