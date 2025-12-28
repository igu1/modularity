from typing import Optional, Dict, Any
from datetime import datetime
class BaseModel:
    def __init__(
        self,
        id: Optional[int] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at)
        }
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseModel':
        return cls(
            id=data.get('id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    @classmethod
    def from_db_row(cls, row: tuple) -> 'BaseModel':
        return cls(
            id=row[0],
            created_at=row[1],
            updated_at=row[2]
        )
    def validate(self) -> tuple[bool, list[str]]:
        errors = []
        if self.id is not None and self.id < 0:
            errors.append("ID cannot be negative")
        return len(errors) == 0, errors
    def __repr__(self) -> str:
        return f"<BaseModel(id={self.id})>"
