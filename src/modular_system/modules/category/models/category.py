from typing import Dict, Any
from sqlalchemy import Column, Integer, ForeignKey, String
from modular_system.database.models import DatabaseModel

class CategoryModel(DatabaseModel):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    def to_dict(self) -> Dict[str, Any]:
        return {'id': self.id, 'name': self.name}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CategoryModel':
        return cls(name=data.get('name', ''))
