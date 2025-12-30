from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class SupportModel(DatabaseModel):
    __tablename__ = 'support_tickets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String(255), nullable=False)
    status = Column(String(20), default='open') # open, in_progress, resolved, closed
    priority = Column(String(20), default='medium')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.subject:
            errors.append("Subject is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at and hasattr(self.created_at, 'isoformat') else str(self.created_at) if self.created_at else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupportModel':
        return cls(
            user_id=data.get('user_id'),
            subject=data.get('subject', ''),
            priority=data.get('priority', 'medium')
        )
    @classmethod
    def from_db_row(cls, row) -> 'SupportModel':
        return cls(
            id=row[0],
            user_id=row[1],
            subject=row[2],
            status=row[3],
            priority=row[4],
            created_at=row[5],
            updated_at=row[6]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<SupportTicket(id={self.id}, subject='{self.subject}', status='{self.status}')>"
