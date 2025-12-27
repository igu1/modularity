"""Database models and base classes."""

from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import declared_attr
from typing import Dict, Any, List, Optional
from .connection import session_scope
from ..logging.logger import CoreLogger

Base = declarative_base()
logger = CoreLogger()


class TimestampMixin:
    """
    Mixin class that adds timestamp fields to models.
    
    This mixin provides created_at and updated_at fields that are
    automatically managed.
    """
    
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class DatabaseModel(Base, TimestampMixin):
    """
    Base model class for all database models.
    
    This class provides common functionality for all models including:
    - Automatic table naming
    - Common CRUD operations
    - Dictionary serialization
    - Soft delete support (optional)
    """
    
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, index=True)
    
    @declared_attr
    def __tablename__(cls):
        """Generate table name from class name."""
        return cls.__name__.lower()
    
    # Class methods for CRUD operations
    @classmethod
    def create(cls, **kwargs) -> Dict[str, Any]:
        """
        Create a new record.
        
        Args:
            **kwargs: Field values for the new record
            
        Returns:
            Dictionary representation of the created record
        """
        with session_scope() as session:
            instance = cls(**kwargs)
            session.add(instance)
            session.flush()
            session.refresh(instance)
            result = instance.to_dict()
            logger.log("database", f"Created {cls.__name__} with ID {result.get('id')}", "debug")
            return result
    
    @classmethod
    def get(cls, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a record by ID.
        
        Args:
            record_id: ID of the record to retrieve
            
        Returns:
            Dictionary representation of the record or None if not found
        """
        with session_scope(commit=False) as session:
            instance = session.query(cls).filter_by(id=record_id).first()
            return instance.to_dict() if instance else None
    
    @classmethod
    def get_by(cls, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Get a record by field values.
        
        Args:
            **kwargs: Field values to match
            
        Returns:
            Dictionary representation of the record or None if not found
        """
        with session_scope(commit=False) as session:
            instance = session.query(cls).filter_by(**kwargs).first()
            return instance.to_dict() if instance else None
    
    @classmethod
    def filter(cls, **kwargs) -> List[Dict[str, Any]]:
        """
        Get records matching field values.
        
        Args:
            **kwargs: Field values to match
            
        Returns:
            List of dictionary representations of matching records
        """
        with session_scope(commit=False) as session:
            instances = session.query(cls).filter_by(**kwargs).all()
            return [instance.to_dict() for instance in instances]
    
    @classmethod
    def all(cls) -> List[Dict[str, Any]]:
        """
        Get all records.
        
        Returns:
            List of dictionary representations of all records
        """
        with session_scope(commit=False) as session:
            instances = session.query(cls).all()
            return [instance.to_dict() for instance in instances]
    
    @classmethod
    def count(cls) -> int:
        """
        Count all records.
        
        Returns:
            Total number of records
        """
        with session_scope(commit=False) as session:
            return session.query(cls).count()
    
    @classmethod
    def exists(cls, **kwargs) -> bool:
        """
        Check if a record exists matching the given criteria.
        
        Args:
            **kwargs: Field values to match
            
        Returns:
            True if record exists, False otherwise
        """
        with session_scope(commit=False) as session:
            return session.query(cls).filter_by(**kwargs).first() is not None
    
    @classmethod
    def update_record(cls, record_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """
        Update a record by ID.
        
        Args:
            record_id: ID of the record to update
            **kwargs: Field values to update
            
        Returns:
            Dictionary representation of the updated record or None if not found
        """
        with session_scope() as session:
            instance = session.query(cls).filter_by(id=record_id).first()
            if instance:
                for key, value in kwargs.items():
                    if hasattr(instance, key):
                        setattr(instance, key, value)
                session.flush()
                session.refresh(instance)
                result = instance.to_dict()
                logger.log("database", f"Updated {cls.__name__} with ID {record_id}", "debug")
                return result
            return None
    
    @classmethod
    def update_by(cls, filter_kwargs: Dict[str, Any], update_kwargs: Dict[str, Any]) -> int:
        """
        Update records matching filter criteria.
        
        Args:
            filter_kwargs: Field values to filter by
            update_kwargs: Field values to update
            
        Returns:
            Number of records updated
        """
        with session_scope() as session:
            result = session.query(cls).filter_by(**filter_kwargs).update(update_kwargs)
            logger.log("database", f"Updated {result} {cls.__name__} records", "debug")
            return result
    
    @classmethod
    def delete_record(cls, record_id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            record_id: ID of the record to delete
            
        Returns:
            True if record was deleted, False if not found
        """
        with session_scope() as session:
            instance = session.query(cls).filter_by(id=record_id).first()
            if instance:
                session.delete(instance)
                logger.log("database", f"Deleted {cls.__name__} with ID {record_id}", "debug")
                return True
            return False
    
    @classmethod
    def delete_by(cls, **kwargs) -> int:
        """
        Delete records matching field values.
        
        Args:
            **kwargs: Field values to match
            
        Returns:
            Number of records deleted
        """
        with session_scope() as session:
            result = session.query(cls).filter_by(**kwargs).delete()
            logger.log("database", f"Deleted {result} {cls.__name__} records", "debug")
            return result
    
    @classmethod
    def paginate(cls, page: int = 1, per_page: int = 10, **kwargs) -> Dict[str, Any]:
        """
        Get paginated results.
        
        Args:
            page: Page number (1-based)
            per_page: Number of items per page
            **kwargs: Filter criteria
            
        Returns:
            Dictionary with pagination info and results
        """
        with session_scope(commit=False) as session:
            query = session.query(cls)
            if kwargs:
                query = query.filter_by(**kwargs)
            
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
    
    # Instance methods
    def update(self, **kwargs) -> Dict[str, Any]:
        """
        Update this instance with new values.
        
        Args:
            **kwargs: Field values to update
            
        Returns:
            Dictionary representation of the updated instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        with session_scope() as session:
            session.add(self)
            session.flush()
            session.refresh(self)
            result = self.to_dict()
            logger.log("database", f"Updated {self.__class__.__name__} with ID {self.id}", "debug")
            return result
    
    def delete(self) -> bool:
        """
        Delete this instance.
        
        Returns:
            True if deleted successfully
        """
        with session_scope() as session:
            session.delete(self)
            logger.log("database", f"Deleted {self.__class__.__name__} with ID {self.id}", "debug")
            return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert instance to dictionary.
        
        Returns:
            Dictionary representation of the instance
        """
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            
            # Handle special types
            if hasattr(value, 'isoformat'):  # datetime objects
                value = value.isoformat()
            elif hasattr(value, 'value'):  # enum objects
                value = value.value
            
            result[column.name] = value
        return result
    
    def refresh(self):
        """Refresh the instance from the database."""
        with session_scope(commit=False) as session:
            session.add(self)
            session.refresh(self)
    
    @classmethod
    def get_table_info(cls) -> Dict[str, Any]:
        """
        Get information about this model's table.
        
        Returns:
            Dictionary with table information
        """
        columns = []
        for column in cls.__table__.columns:
            columns.append({
                'name': column.name,
                'type': str(column.type),
                'nullable': column.nullable,
                'primary_key': column.primary_key,
                'default': str(column.default) if column.default else None
            })
        
        return {
            'table_name': cls.__tablename__,
            'columns': columns,
            'column_count': len(columns)
        }


class SoftDeleteMixin:
    """
    Mixin class that adds soft delete functionality to models.
    
    This mixin adds a deleted_at field and modifies queries to exclude
    soft-deleted records by default.
    """
    
    deleted_at = Column(DateTime, nullable=True)
    
    def soft_delete(self):
        """Mark this record as deleted."""
        from datetime import datetime
        self.deleted_at = datetime.utcnow()
        with session_scope() as session:
            session.add(self)
        logger.log("database", f"Soft deleted {self.__class__.__name__} with ID {self.id}", "debug")
    
    def restore(self):
        """Restore this soft-deleted record."""
        self.deleted_at = None
        with session_scope() as session:
            session.add(self)
        logger.log("database", f"Restored {self.__class__.__name__} with ID {self.id}", "debug")
    
    @classmethod
    def get_active(cls, **kwargs):
        """Get only active (non-deleted) records."""
        kwargs['deleted_at'] = None
        return cls.filter(**kwargs)
    
    @classmethod
    def get_deleted(cls, **kwargs):
        """Get only deleted records."""
        kwargs['deleted_at__ne'] = None  # This would need custom implementation
        # For now, return all and filter in Python
        all_records = cls.filter(**kwargs)
        return [record for record in all_records if record.get('deleted_at') is not None]
