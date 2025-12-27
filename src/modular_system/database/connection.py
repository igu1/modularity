"""Database connection management and session handling."""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Optional, Generator, Any, Dict
from contextlib import contextmanager
from ..logging.logger import CoreLogger


# Global variables for database connection
_engine: Optional[Any] = None
_SessionLocal: Optional[sessionmaker] = None
Base = declarative_base()
metadata = MetaData()
logger = CoreLogger()


def init_db(database_url: str = "sqlite:///modular_system.db", echo: bool = False) -> None:
    """
    Initialize the database connection.
    
    This function should be called once at application startup to set up
    the database engine and session factory.
    
    Args:
        database_url: Database connection URL
        echo: Whether to enable SQLAlchemy query logging
    """
    global _engine, _SessionLocal
    
    try:
        _engine = create_engine(database_url, echo=echo)
        _SessionLocal = sessionmaker(bind=_engine)
        
        # Create all tables
        Base.metadata.create_all(bind=_engine)
        
        logger.log("database", f"Database initialized with URL: {database_url}", "info")
        
    except Exception as e:
        logger.log("database", f"Failed to initialize database: {e}", "error")
        raise


def get_engine() -> Any:
    """
    Get the database engine.
    
    Returns:
        SQLAlchemy engine instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if not _engine:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _engine


def get_session() -> Session:
    """
    Get a database session.
    
    Returns:
        SQLAlchemy session instance
        
    Raises:
        RuntimeError: If database not initialized
    """
    if not _SessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionLocal()


@contextmanager
def session_scope(commit: bool = True) -> Generator[Session, None, None]:
    """
    Context manager for database sessions with automatic commit/rollback.
    
    Args:
        commit: Whether to commit the transaction automatically
        
    Yields:
        SQLAlchemy session instance
        
    Example:
        with session_scope() as session:
            user = User(name="John")
            session.add(user)
            # Automatic commit on success, rollback on exception
    """
    session = get_session()
    try:
        yield session
        if commit:
            session.commit()
            logger.log("database", "Transaction committed", "debug")
    except Exception as e:
        session.rollback()
        logger.log("database", f"Transaction rolled back due to error: {e}", "error")
        raise
    finally:
        session.close()


class DatabaseService:
    """
    Service class for database operations.
    
    This class provides a high-level interface for database operations
    and can be registered as a service in the registry.
    """
    
    def __init__(self, database_url: str = "sqlite:///modular_system.db", echo: bool = False):
        """
        Initialize the database service.
        
        Args:
            database_url: Database connection URL
            echo: Whether to enable SQLAlchemy query logging
        """
        self.database_url = database_url
        self.echo = echo
        self._initialized = False
    
    def initialize(self):
        """Initialize the database connection."""
        if not self._initialized:
            init_db(self.database_url, self.echo)
            self._initialized = True
            logger.log("database", "Database service initialized", "info")
    
    def get_session(self) -> Session:
        """Get a database session."""
        if not self._initialized:
            self.initialize()
        return get_session()
    
    def get_engine(self) -> Any:
        """Get the database engine."""
        if not self._initialized:
            self.initialize()
        return get_engine()
    
    def create_tables(self):
        """Create all database tables."""
        engine = self.get_engine()
        Base.metadata.create_all(bind=engine)
        logger.log("database", "Database tables created", "info")
    
    def drop_tables(self):
        """Drop all database tables."""
        engine = self.get_engine()
        Base.metadata.drop_all(bind=engine)
        logger.log("database", "Database tables dropped", "warning")
    
    def reset_database(self):
        """Reset the database by dropping and recreating all tables."""
        self.drop_tables()
        self.create_tables()
        logger.log("database", "Database reset completed", "warning")
    
    def check_connection(self) -> bool:
        """
        Check if database connection is working.
        
        Returns:
            True if connection is working, False otherwise
        """
        try:
            with session_scope(commit=False) as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.log("database", f"Database connection check failed: {e}", "error")
            return False
    
    def get_table_info(self) -> Dict[str, Any]:
        """
        Get information about database tables.
        
        Returns:
            Dictionary with table information
        """
        try:
            engine = self.get_engine()
            inspector = engine.inspect(engine)
            
            tables = {}
            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                tables[table_name] = {
                    'columns': [col['name'] for col in columns],
                    'column_count': len(columns)
                }
            
            return {
                'table_count': len(tables),
                'tables': tables
            }
        except Exception as e:
            logger.log("database", f"Error getting table info: {e}", "error")
            return {'table_count': 0, 'tables': {}}


# Global database service instance
db_service = DatabaseService()


def get_database_service() -> DatabaseService:
    """Get the global database service instance."""
    return db_service
