from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from typing import Dict, Any, List, Optional
from .connection import session_scope

Base = declarative_base()

class DatabaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    @declared_attr
    def __tablename__(cls): return cls.__name__.lower()

    @classmethod
    def create(cls, **kwargs) -> Dict[str, Any]:
        with session_scope() as s:
            i = cls(**kwargs); s.add(i); s.flush(); s.refresh(i)
            return i.to_dict()

    @classmethod
    def get(cls, rid: int) -> Optional[Dict[str, Any]]:
        with session_scope(False) as s:
            i = s.query(cls).get(rid)
            return i.to_dict() if i else None

    @classmethod
    def get_by(cls, **kwargs) -> Optional[Dict[str, Any]]:
        with session_scope(False) as s:
            i = s.query(cls).filter_by(**kwargs).first()
            return i.to_dict() if i else None

    @classmethod
    def all(cls) -> List[Dict[str, Any]]:
        with session_scope(False) as s: return [i.to_dict() for i in s.query(cls).all()]

    @classmethod
    def update_record(cls, rid: int, **kwargs) -> Optional[Dict[str, Any]]:
        with session_scope() as s:
            i = s.query(cls).get(rid)
            if i:
                for k, v in kwargs.items():
                    if hasattr(i, k): setattr(i, k, v)
                s.flush(); s.refresh(i); return i.to_dict()
            return None

    @classmethod
    def delete_record(cls, rid: int) -> bool:
        with session_scope() as s:
            i = s.query(cls).get(rid)
            if i: s.delete(i); return True
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: (getattr(self, c.name).isoformat() if hasattr(getattr(self, c.name), 'isoformat') else getattr(self, c.name)) for c in self.__table__.columns}
