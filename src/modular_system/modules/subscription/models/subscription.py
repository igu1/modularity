from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class SubscriptionModel(DatabaseModel):
    __tablename__ = 'subscriptions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    plan_name = Column(String(100), nullable=False)
    status = Column(String(20), default='active') # active, cancelled, expired
    start_date = Column(DateTime, default=datetime.now)
    next_billing_date = Column(DateTime)
    price_per_period = Column(Integer)
    billing_period = Column(String(20), default='monthly')
    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.plan_name:
            errors.append("Plan name is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'plan': self.plan_name,
            'status': self.status,
            'price': self.price_per_period,
            'period': self.billing_period,
            'next_billing': self.next_billing_date.isoformat() if self.next_billing_date else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SubscriptionModel':
        return cls(
            user_id=data.get('user_id'),
            plan_name=data.get('plan_name', ''),
            price_per_period=data.get('price'),
            billing_period=data.get('billing_period', 'monthly')
        )
    @classmethod
    def from_db_row(cls, row) -> 'SubscriptionModel':
        return cls(
            id=row[0],
            user_id=row[1],
            plan_name=row[2],
            status=row[3],
            start_date=row[4],
            next_billing_date=row[5],
            price_per_period=row[6],
            billing_period=row[7]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Subscription(user={self.user_id}, plan='{self.plan_name}', status='{self.status}')>"
