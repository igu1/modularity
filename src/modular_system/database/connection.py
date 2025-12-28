from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Optional, Generator, Any, Dict
from contextlib import contextmanager
from ..logging.logger import CoreLogger
_engine: Optional[Any] = None
_SessionLocal: Optional[sessionmaker] = None
Base = declarative_base()
metadata = MetaData()
logger = CoreLogger()
def init_db(database_url: str = "sqlite:///modular_system.db", echo: bool = False) -> None:
    global _engine, _SessionLocal
    try:
        _engine = create_engine(database_url, echo=echo)
        _SessionLocal = sessionmaker(bind=_engine)
        Base.metadata.create_all(bind=_engine)
        logger.log("database", f"Database initialized with URL: {database_url}", "info")
    except Exception as e:
        logger.log("database", f"Failed to initialize database: {e}", "error")
        raise
def get_engine() -> Any:
    if not _engine:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _engine
def get_session() -> Session:
    if not _SessionLocal:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _SessionLocal()
@contextmanager
def session_scope(commit: bool = True) -> Generator[Session, None, None]:
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
    def __init__(self, database_url: str = "sqlite:///modular_system.db", echo: bool = False):
        self.database_url = database_url
        self.echo = echo
        self._initialized = False
    def initialize(self):
        if not self._initialized:
            init_db(self.database_url, self.echo)
            self._initialized = True
            logger.log("database", "Database service initialized", "info")
    def get_session(self) -> Session:
        if not self._initialized:
            self.initialize()
        return get_session()
    def get_engine(self) -> Any:
        if not self._initialized:
            self.initialize()
        return get_engine()
    def create_tables(self):
        engine = self.get_engine()
        Base.metadata.create_all(bind=engine)
        logger.log("database", "Database tables created", "info")
    def drop_tables(self):
        engine = self.get_engine()
        Base.metadata.drop_all(bind=engine)
        logger.log("database", "Database tables dropped", "warning")
    def reset_database(self):
        self.drop_tables()
        self.create_tables()
        logger.log("database", "Database reset completed", "warning")
    def check_connection(self) -> bool:
        try:
            with session_scope(commit=False) as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.log("database", f"Database connection check failed: {e}", "error")
            return False
    def get_table_info(self) -> Dict[str, Any]:
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
db_service = DatabaseService()
def get_database_service() -> DatabaseService:
    return db_service
