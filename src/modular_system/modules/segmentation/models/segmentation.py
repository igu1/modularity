from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class SegmentationModel(DatabaseModel):
    __tablename__ = 'segmentations'
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
    def from_dict(cls, data: Dict[str, Any]) -> 'SegmentationModel':
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )

    @classmethod
    def from_db_row(cls, row) -> 'SegmentationModel':
        return cls(
            id=row[0],
            name=row[1],
            description=row[2],
            is_active=bool(row[3]) if row[3] is not None else True
        )

    def __repr__(self) -> str:
        return f"<Segmentation(id={self.id}, name='{self.name}')>"

class SegmentModel(DatabaseModel):
    __tablename__ = 'segments'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    rules_json = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Name is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'rules': self.rules_json,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SegmentModel':
        return cls(
            name=data.get('name', ''),
            rules_json=data.get('rules')
        )
    @classmethod
    def from_db_row(cls, row) -> 'SegmentModel':
        return cls(
            id=row[0],
            name=row[1],
            rules_json=row[2],
            created_at=row[3]
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<Segment(id={self.id}, name='{self.name}')>"
