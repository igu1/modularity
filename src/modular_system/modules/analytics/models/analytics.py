from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class AnalyticsModel(DatabaseModel):
    __tablename__ = 'analytics_events'
    id = Column(Integer, primary_key=True)
    event_type = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    path = Column(String(255))
    metadata_json = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.event_type:
            errors.append("Event type is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.event_type,
            'user_id': self.user_id,
            'path': self.path,
            'metadata': self.metadata_json,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnalyticsModel':
        return cls(
            event_type=data.get('event_type'),
            user_id=data.get('user_id'),
            path=data.get('path'),
            metadata_json=json.dumps(data.get('metadata', {}))
        )
    @classmethod
    def from_db_row(cls, row) -> 'AnalyticsModel':
        return cls(
            id=row[0],
            event_type=row[1],
            user_id=row[2],
            path=row[3],
            metadata_json=row[4],
            created_at=row[5]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<AnalyticsEvent(type='{self.event_type}', path='{self.path}')>"
