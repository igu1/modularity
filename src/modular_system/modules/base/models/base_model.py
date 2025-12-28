from typing import Optional, Dict, Any
from datetime import datetime

class BaseModel:
    def __init__(self, id: int = None, created_at: datetime = None, updated_at: datetime = None):
        self.id, self.created_at, self.updated_at = id, created_at or datetime.now(), updated_at or datetime.now()
    def to_dict(self) -> Dict[str, Any]:
        return {'id': self.id, 'created_at': str(self.created_at), 'updated_at': str(self.updated_at)}
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(id=data.get('id'), created_at=data.get('created_at'), updated_at=data.get('updated_at'))
    def __repr__(self): return f"<BaseModel(id={self.id})>"
