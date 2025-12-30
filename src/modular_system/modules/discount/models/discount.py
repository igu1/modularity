from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class DiscountModel(DatabaseModel):
    __tablename__ = 'discounts'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
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
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiscountModel':
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )

    @classmethod
    def from_db_row(cls, row) -> 'DiscountModel':
        return cls(
            id=row[0],
            name=row[1],
            description=row[2],
            is_active=bool(row[3]) if row[3] is not None else True
        )

    def __repr__(self) -> str:
        return f"<Discount(id={self.id}, name='{self.name}')>"

class CouponModel(DatabaseModel):
    __tablename__ = 'coupons'
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_type = Column(String(20), nullable=False) # percentage, fixed
    discount_value = Column(Integer, nullable=False)
    min_purchase = Column(Integer, default=0)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.code or len(self.code.strip()) == 0:
            errors.append("Code is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'code': self.code,
            'discount_type': self.discount_type,
            'discount_value': self.discount_value,
            'min_purchase': self.min_purchase,
            'is_active': self.is_active,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CouponModel':
        return cls(
            code=data.get('code', ''),
            discount_type=data.get('discount_type', 'percentage'),
            discount_value=data.get('discount_value', 0),
            min_purchase=data.get('min_purchase', 0),
            is_active=data.get('is_active', True)
        )
    @classmethod
    def from_db_row(cls, row) -> 'CouponModel':
        return cls(
            id=row[0],
            code=row[1],
            discount_type=row[2],
            discount_value=row[3],
            min_purchase=row[4],
            is_active=row[6]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Coupon(id={self.id}, code='{self.code}')>"
