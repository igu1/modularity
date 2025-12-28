from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel

class OrganizationModel(DatabaseModel):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    domain = Column(String(255), unique=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Name is required")
        if not self.slug or len(self.slug.strip()) == 0:
            errors.append("Slug is required")
        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'domain': self.domain,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OrganizationModel':
        return cls(
            name=data.get('name', ''),
            slug=data.get('slug', ''),
            domain=data.get('domain'),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )

    @classmethod
    def from_db_row(cls, row) -> 'OrganizationModel':
        return cls(
            id=row[0] if len(row) > 0 else None,
            name=row[1] if len(row) > 1 else '',
            slug=row[2] if len(row) > 2 else '',
            domain=row[3] if len(row) > 3 else None,
            description=row[4] if len(row) > 4 else '',
            is_active=row[5] if len(row) > 5 else True,
            created_at=row[6] if len(row) > 6 else None,
            updated_at=row[7] if len(row) > 7 else None
        )

    def update_timestamp(self):
        self.updated_at = datetime.now()

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}')>"
