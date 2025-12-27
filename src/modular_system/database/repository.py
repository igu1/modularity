                                                                

from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Optional, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc
from .models import DatabaseModel
from .connection import session_scope
from ..logging.logger import CoreLogger

T = TypeVar('T', bound=DatabaseModel)
logger = CoreLogger()


class BaseRepository(ABC, Generic[T]):
\
\
\
\
\
       
    
    def __init__(self, model_class: Type[T]):
\
\
\
\
\
           
        self.model_class = model_class
        self.model_name = model_class.__name__
    
                           
    def create(self, **kwargs) -> Dict[str, Any]:
                                  
        return self.model_class.create(**kwargs)
    
    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
                                 
        return self.model_class.get(record_id)
    
    def get_by(self, **kwargs) -> Optional[Dict[str, Any]]:
                                           
        return self.model_class.get_by(**kwargs)
    
    def get_all(self) -> List[Dict[str, Any]]:
                              
        return self.model_class.all()
    
    def filter(self, **kwargs) -> List[Dict[str, Any]]:
                                                
        return self.model_class.filter(**kwargs)
    
    def update(self, record_id: int, **kwargs) -> Optional[Dict[str, Any]]:
                                    
        return self.model_class.update_record(record_id, **kwargs)
    
    def delete(self, record_id: int) -> bool:
                                    
        return self.model_class.delete_record(record_id)
    
    def exists(self, **kwargs) -> bool:
                                       
        return self.model_class.exists(**kwargs)
    
    def count(self) -> int:
                                
        return self.model_class.count()
    
                               
    def find_where(self, *conditions) -> List[Dict[str, Any]]:
\
\
\
\
\
\
\
\
           
        with session_scope(commit=False) as session:
            query = session.query(self.model_class)
            if conditions:
                query = query.filter(and_(*conditions))
            instances = query.all()
            return [instance.to_dict() for instance in instances]
    
    def find_one_where(self, *conditions) -> Optional[Dict[str, Any]]:
\
\
\
\
\
\
\
\
           
        with session_scope(commit=False) as session:
            query = session.query(self.model_class)
            if conditions:
                query = query.filter(and_(*conditions))
            instance = query.first()
            return instance.to_dict() if instance else None
    
    def search(self, search_term: str, search_fields: List[str]) -> List[Dict[str, Any]]:
\
\
\
\
\
\
\
\
\
           
        with session_scope(commit=False) as session:
            query = session.query(self.model_class)
            
                                                   
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model_class, field):
                    field_attr = getattr(self.model_class, field)
                    search_conditions.append(field_attr.like(f'%{search_term}%'))
            
            if search_conditions:
                query = query.filter(or_(*search_conditions))
            
            instances = query.all()
            return [instance.to_dict() for instance in instances]
    
    def order_by(self, field: str, descending: bool = False) -> List[Dict[str, Any]]:
\
\
\
\
\
\
\
\
\
           
        with session_scope(commit=False) as session:
            query = session.query(self.model_class)
            
            if hasattr(self.model_class, field):
                field_attr = getattr(self.model_class, field)
                if descending:
                    query = query.order_by(desc(field_attr))
                else:
                    query = query.order_by(asc(field_attr))
            
            instances = query.all()
            return [instance.to_dict() for instance in instances]
    
    def paginate(self, page: int = 1, per_page: int = 10, 
                 order_by: Optional[str] = None, 
                 descending: bool = False,
                 **kwargs) -> Dict[str, Any]:
\
\
\
\
\
\
\
\
\
\
\
\
           
        with session_scope(commit=False) as session:
            query = session.query(self.model_class)
            
                           
            if kwargs:
                query = query.filter_by(**kwargs)
            
                            
            if order_by and hasattr(self.model_class, order_by):
                field_attr = getattr(self.model_class, order_by)
                if descending:
                    query = query.order_by(desc(field_attr))
                else:
                    query = query.order_by(asc(field_attr))
            
                             
            total = query.count()
            
                              
            items = query.offset((page - 1) * per_page).limit(per_page).all()
            
            return {
                'items': [item.to_dict() for item in items],
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': (total + per_page - 1) // per_page,
                'has_next': page * per_page < total,
                'has_prev': page > 1
            }
    
    def bulk_create(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
\
\
\
\
\
\
\
\
           
        with session_scope() as session:
            instances = [self.model_class(**item) for item in items]
            session.add_all(instances)
            session.flush()
            
                                                    
            for instance in instances:
                session.refresh(instance)
            
            results = [instance.to_dict() for instance in instances]
            logger.log("database", f"Bulk created {len(results)} {self.model_name} records", "debug")
            return results
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
\
\
\
\
\
\
\
\
           
        with session_scope() as session:
            updated_count = 0
            for update_data in updates:
                if 'id' in update_data:
                    record_id = update_data.pop('id')
                    result = session.query(self.model_class).filter_by(id=record_id).update(update_data)
                    updated_count += result
            
            logger.log("database", f"Bulk updated {updated_count} {self.model_name} records", "debug")
            return updated_count
    
    def bulk_delete(self, record_ids: List[int]) -> int:
\
\
\
\
\
\
\
\
           
        with session_scope() as session:
            result = session.query(self.model_class).filter(
                self.model_class.id.in_(record_ids)
            ).delete(synchronize_session=False)
            
            logger.log("database", f"Bulk deleted {result} {self.model_name} records", "debug")
            return result
    
                              
    def get_field_values(self, field: str, distinct: bool = True) -> List[Any]:
\
\
\
\
\
\
\
\
\
           
        with session_scope(commit=False) as session:
            query = session.query(getattr(self.model_class, field))
            if distinct:
                query = query.distinct()
            values = query.all()
            return [value[0] for value in values]
    
    def count_by_field(self, field: str) -> Dict[str, int]:
\
\
\
\
\
\
\
\
           
        with session_scope(commit=False) as session:
            from sqlalchemy import func
            
            query = session.query(
                getattr(self.model_class, field),
                func.count(self.model_class.id)
            ).group_by(getattr(self.model_class, field))
            
            results = query.all()
            return {str(value): count for value, count in results}
    
    def get_statistics(self) -> Dict[str, Any]:
\
\
\
\
\
           
        with session_scope(commit=False) as session:
            from sqlalchemy import func
            
                          
            total_count = session.query(func.count(self.model_class.id)).scalar()
            
                            
            table_info = self.model_class.get_table_info()
            
            return {
                'model_name': self.model_name,
                'total_records': total_count,
                'table_info': table_info
            }


class RepositoryManager:
\
\
\
\
\
       
    
    def __init__(self):
                                                
        self._repositories: Dict[str, BaseRepository] = {}
    
    def register_repository(self, name: str, repository: BaseRepository):
\
\
\
\
\
\
           
        self._repositories[name] = repository
        logger.log("database", f"Registered repository: {name}", "debug")
    
    def get_repository(self, name: str) -> Optional[BaseRepository]:
\
\
\
\
\
\
\
\
           
        return self._repositories.get(name)
    
    def list_repositories(self) -> List[str]:
                                                      
        return list(self._repositories.keys())
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
                                                             
        statistics = {}
        for name, repository in self._repositories.items():
            try:
                statistics[name] = repository.get_statistics()
            except Exception as e:
                logger.log("database", f"Error getting statistics for {name}: {e}", "error")
                statistics[name] = {'error': str(e)}
        
        return statistics


                                    
repository_manager = RepositoryManager()


def get_repository_manager() -> RepositoryManager:
                                                     
    return repository_manager
