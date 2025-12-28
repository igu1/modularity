from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from sqlalchemy import and_, or_
from .models import DatabaseModel
from .connection import session_scope

T = TypeVar('T', bound=DatabaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, model_cls: Type[T]): self.cls = model_cls
    def create(self, **kwargs) -> Dict: return self.cls.create(**kwargs)
    def get(self, rid: int) -> Optional[Dict]: return self.cls.get(rid)
    def all(self) -> List[Dict]: return self.cls.all()
    def update(self, rid: int, **kwargs) -> Optional[Dict]: return self.cls.update_record(rid, **kwargs)
    def delete(self, rid: int) -> bool: return self.cls.delete_record(rid)

    def find(self, *conds) -> List[Dict]:
        with session_scope(False) as s:
            return [i.to_dict() for i in s.query(self.cls).filter(and_(*conds)).all()]

class RepositoryManager:
    def __init__(self): self._repos: Dict[str, Any] = {}
    def reg(self, name: str, repo: Any): self._repos[name] = repo
    def get(self, name: str) -> Optional[Any]: return self._repos.get(name)

manager = RepositoryManager()
def get_repo_manager(): return manager
