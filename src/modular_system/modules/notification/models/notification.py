from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class NotificationModel(DatabaseModel):
    __tablename__ = 'notifications'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False)
    message = Column(Text)
    type = Column(String(50), default='info')
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.title:
            errors.append("Title is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NotificationModel':
        return cls(
            user_id=data.get('user_id'),
            title=data.get('title', ''),
            message=data.get('message', ''),
            type=data.get('type', 'info')
        )
    @classmethod
    def from_db_row(cls, row) -> 'NotificationModel':
        return cls(
            id=row[0],
            user_id=row[1],
            title=row[2],
            message=row[3],
            type=row[4],
            is_read=row[5],
            created_at=row[6]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, user={self.user_id}, title='{self.title}')>"
