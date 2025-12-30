from sqlalchemy import Column, String, JSON, Boolean
from modular_system.database.models import DatabaseModel
from typing import Dict, Any

class UserModel(DatabaseModel):
    __tablename__ = 'users'
    
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    metadata_fields = Column(JSON, default={})

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        if 'password' in data:
            del data['password']
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserModel':
        return cls(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            is_active=data.get('is_active', True),
            metadata_fields=data.get('metadata_fields', {})
        )
