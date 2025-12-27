"""Repository pattern implementation for database operations."""

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
    """
    Abstract base repository implementing the repository pattern.
    
    This class provides a standardized interface for database operations
    and can be extended for specific model types.
    """
    
    def __init__(self, model_class: Type[T]):
        """
        Initialize the repository.
        
        Args:
            model_class: The model class this repository manages
        """
        self.model_class = model_class
        self.model_name = model_class.__name__
    
    # Basic CRUD operations
    def create(self, **kwargs) -> Dict[str, Any]:
        """Create a new record."""
        return self.model_class.create(**kwargs)
    
    def get_by_id(self, record_id: int) -> Optional[Dict[str, Any]]:
        """Get a record by ID."""
        return self.model_class.get(record_id)
    
    def get_by(self, **kwargs) -> Optional[Dict[str, Any]]:
        """Get a record by field values."""
        return self.model_class.get_by(**kwargs)
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all records."""
        return self.model_class.all()
    
    def filter(self, **kwargs) -> List[Dict[str, Any]]:
        """Get records matching field values."""
        return self.model_class.filter(**kwargs)
    
    def update(self, record_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a record by ID."""
        return self.model_class.update_record(record_id, **kwargs)
    
    def delete(self, record_id: int) -> bool:
        """Delete a record by ID."""
        return self.model_class.delete_record(record_id)
    
    def exists(self, **kwargs) -> bool:
        """Check if a record exists."""
        return self.model_class.exists(**kwargs)
    
    def count(self) -> int:
        """Count all records."""
        return self.model_class.count()
    
    # Advanced query operations
    def find_where(self, *conditions) -> List[Dict[str, Any]]:
        """
        Find records using SQLAlchemy conditions.
        
        Args:
            *conditions: SQLAlchemy condition objects
            
        Returns:
            List of matching records
        """
        with session_scope(commit=False) as session:
            query = session.query(self.model_class)
            if conditions:
                query = query.filter(and_(*conditions))
            instances = query.all()
            return [instance.to_dict() for instance in instances]
    
    def find_one_where(self, *conditions) -> Optional[Dict[str, Any]]:
        """
        Find one record using SQLAlchemy conditions.
        
        Args:
            *conditions: SQLAlchemy condition objects
            
        Returns:
            First matching record or None
        """
        with session_scope(commit=False) as session:
            query = session.query(self.model_class)
            if conditions:
                query = query.filter(and_(*conditions))
            instance = query.first()
            return instance.to_dict() if instance else None
    
    def search(self, search_term: str, search_fields: List[str]) -> List[Dict[str, Any]]:
        """
        Search for records in specified fields.
        
        Args:
            search_term: Term to search for
            search_fields: List of field names to search in
            
        Returns:
            List of matching records
        """
        with session_scope(commit=False) as session:
            query = session.query(self.model_class)
            
            # Build OR conditions for search fields
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
        """
        Get all records ordered by a field.
        
        Args:
            field: Field name to order by
            descending: Whether to sort in descending order
            
        Returns:
            Ordered list of records
        """
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
        """
        Get paginated results with optional ordering.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            order_by: Field to order by
            descending: Whether to sort in descending order
            **kwargs: Filter criteria
            
        Returns:
            Dictionary with pagination info and results
        """
        with session_scope(commit=False) as session:
            query = session.query(self.model_class)
            
            # Apply filters
            if kwargs:
                query = query.filter_by(**kwargs)
            
            # Apply ordering
            if order_by and hasattr(self.model_class, order_by):
                field_attr = getattr(self.model_class, order_by)
                if descending:
                    query = query.order_by(desc(field_attr))
                else:
                    query = query.order_by(asc(field_attr))
            
            # Get total count
            total = query.count()
            
            # Apply pagination
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
        """
        Create multiple records at once.
        
        Args:
            items: List of dictionaries with field values
            
        Returns:
            List of created records
        """
        with session_scope() as session:
            instances = [self.model_class(**item) for item in items]
            session.add_all(instances)
            session.flush()
            
            # Refresh all instances to get their IDs
            for instance in instances:
                session.refresh(instance)
            
            results = [instance.to_dict() for instance in instances]
            logger.log("database", f"Bulk created {len(results)} {self.model_name} records", "debug")
            return results
    
    def bulk_update(self, updates: List[Dict[str, Any]]) -> int:
        """
        Update multiple records at once.
        
        Args:
            updates: List of dictionaries with 'id' and field values to update
            
        Returns:
            Number of records updated
        """
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
        """
        Delete multiple records at once.
        
        Args:
            record_ids: List of record IDs to delete
            
        Returns:
            Number of records deleted
        """
        with session_scope() as session:
            result = session.query(self.model_class).filter(
                self.model_class.id.in_(record_ids)
            ).delete(synchronize_session=False)
            
            logger.log("database", f"Bulk deleted {result} {self.model_name} records", "debug")
            return result
    
    # Statistics and analytics
    def get_field_values(self, field: str, distinct: bool = True) -> List[Any]:
        """
        Get all values for a specific field.
        
        Args:
            field: Field name
            distinct: Whether to return only distinct values
            
        Returns:
            List of field values
        """
        with session_scope(commit=False) as session:
            query = session.query(getattr(self.model_class, field))
            if distinct:
                query = query.distinct()
            values = query.all()
            return [value[0] for value in values]
    
    def count_by_field(self, field: str) -> Dict[str, int]:
        """
        Count records grouped by field values.
        
        Args:
            field: Field name to group by
            
        Returns:
            Dictionary mapping field values to counts
        """
        with session_scope(commit=False) as session:
            from sqlalchemy import func
            
            query = session.query(
                getattr(self.model_class, field),
                func.count(self.model_class.id)
            ).group_by(getattr(self.model_class, field))
            
            results = query.all()
            return {str(value): count for value, count in results}
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get basic statistics for this model.
        
        Returns:
            Dictionary with statistics
        """
        with session_scope(commit=False) as session:
            from sqlalchemy import func
            
            # Basic counts
            total_count = session.query(func.count(self.model_class.id)).scalar()
            
            # Get table info
            table_info = self.model_class.get_table_info()
            
            return {
                'model_name': self.model_name,
                'total_records': total_count,
                'table_info': table_info
            }


class RepositoryManager:
    """
    Manager class for handling multiple repositories.
    
    This class provides a centralized way to manage and access
    different repositories for various models.
    """
    
    def __init__(self):
        """Initialize the repository manager."""
        self._repositories: Dict[str, BaseRepository] = {}
    
    def register_repository(self, name: str, repository: BaseRepository):
        """
        Register a repository.
        
        Args:
            name: Name to register the repository under
            repository: Repository instance
        """
        self._repositories[name] = repository
        logger.log("database", f"Registered repository: {name}", "debug")
    
    def get_repository(self, name: str) -> Optional[BaseRepository]:
        """
        Get a registered repository.
        
        Args:
            name: Name of the repository
            
        Returns:
            Repository instance or None if not found
        """
        return self._repositories.get(name)
    
    def list_repositories(self) -> List[str]:
        """Get list of registered repository names."""
        return list(self._repositories.keys())
    
    def get_all_statistics(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all registered repositories."""
        statistics = {}
        for name, repository in self._repositories.items():
            try:
                statistics[name] = repository.get_statistics()
            except Exception as e:
                logger.log("database", f"Error getting statistics for {name}: {e}", "error")
                statistics[name] = {'error': str(e)}
        
        return statistics


# Global repository manager instance
repository_manager = RepositoryManager()


def get_repository_manager() -> RepositoryManager:
    """Get the global repository manager instance."""
    return repository_manager
