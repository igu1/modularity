from typing import Dict, Any
from sqlalchemy import Column, Integer, String, Text
from modular_system.database.models import DatabaseModel

class OrganizationModel(DatabaseModel):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    domain = Column(String(255), unique=True)
    description = Column(Text)

    def validate(self):
        errs = []
        if not self.name or not self.name.strip(): errs.append("Name required")
        if not self.slug or not self.slug.strip(): errs.append("Slug required")
        return not errs, errs

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(name=data.get('name', ''), slug=data.get('slug', ''), domain=data.get('domain'), description=data.get('description', ''), is_active=data.get('is_active', True))

    def __repr__(self): return f"<Org(id={self.id}, name='{self.name}')>"
