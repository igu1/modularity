from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from typing import Optional, Generator, Any, Dict
from contextlib import contextmanager

_eng, _Session, Base = None, None, declarative_base()

def init_db(url: str = "sqlite:///modular_system.db", echo: bool = False):
    global _eng, _Session
    _eng = create_engine(url, echo=echo)
    _Session = sessionmaker(bind=_eng)
    Base.metadata.create_all(bind=_eng)

def get_session() -> Session:
    if not _Session: raise RuntimeError("DB not init")
    return _Session()

@contextmanager
def session_scope(commit: bool = True) -> Generator[Session, None, None]:
    s = get_session()
    try:
        yield s
        if commit: s.commit()
    except: s.rollback(); raise
    finally: s.close()

class DatabaseService:
    def __init__(self, url: str = "sqlite:///modular_system.db", echo: bool = False):
        self.url, self.echo, self._init = url, echo, False
    def initialize(self):
        if not self._init: init_db(self.url, self.echo); self._init = True
    def get_session(self) -> Session: self.initialize(); return get_session()
    def get_engine(self) -> Any: self.initialize(); return _eng
    def check_connection(self) -> bool:
        try:
            with session_scope(False) as s: s.execute("SELECT 1"); return True
        except: return False

def get_engine() -> Any: return _eng

db_service = DatabaseService()
def get_database_service() -> DatabaseService: return db_service
