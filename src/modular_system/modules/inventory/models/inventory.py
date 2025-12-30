from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class InventoryModel(DatabaseModel):
    __tablename__ = 'inventory_thresholds'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), unique=True, nullable=False)
    min_stock = Column(Integer, default=5)
    alert_email = Column(String(255))
    is_active = Column(Boolean, default=True)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if self.product_id is None:
            errors.append("Product ID is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'product_id': self.product_id,
            'min_stock': self.min_stock,
            'alert_email': self.alert_email,
            'is_active': self.is_active
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InventoryModel':
        return cls(
            product_id=data.get('product_id'),
            min_stock=data.get('min_stock', 5),
            alert_email=data.get('alert_email')
        )
    @classmethod
    def from_db_row(cls, row) -> 'InventoryModel':
        return cls(
            id=row[0],
            product_id=row[1],
            min_stock=row[2],
            alert_email=row[3],
            is_active=row[4]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<InventoryAlert(product_id={self.product_id}, min={self.min_stock})>"
