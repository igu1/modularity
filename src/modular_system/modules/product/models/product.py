from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class ProductModel(DatabaseModel):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, nullable=False)
    category_id = Column(Integer)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Integer, default=0)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Name is required")
        if self.organization_id is None:
            errors.append("Organization ID is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'organization_id': self.organization_id,
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProductModel':
        return cls(
            organization_id=data.get('organization_id'),
            category_id=data.get('category_id'),
            name=data.get('name', ''),
            description=data.get('description', ''),
            price=data.get('price', 0),
            stock=data.get('stock', 0),
            is_active=data.get('is_active', True)
        )
    @classmethod
    def from_db_row(cls, row) -> 'ProductModel':
        return cls(
            id=row[0] if len(row) > 0 else None,
            organization_id=row[1] if len(row) > 1 else None,
            category_id=row[2] if len(row) > 2 else None,
            name=row[3] if len(row) > 3 else '',
            description=row[4] if len(row) > 4 else '',
            price=row[5] if len(row) > 5 else 0,
            stock=row[6] if len(row) > 6 else 0,
            is_active=row[7] if len(row) > 7 else True,
            created_at=row[8] if len(row) > 8 else None,
            updated_at=row[9] if len(row) > 9 else None
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name='{self.name}')>"
