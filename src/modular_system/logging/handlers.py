import os, sys, logging
from logging.handlers import RotatingFileHandler
from typing import Optional, TextIO

class ConsoleHandler:
    def __init__(self, stream: Optional[TextIO] = None, level: str = "INFO"):
        self.handler = logging.StreamHandler(stream or sys.stdout)
        self.handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    def get_handler(self) -> logging.Handler: return self.handler

class FileHandler:
    def __init__(self, filename: str, level: str = "INFO", mode: str = 'a', encoding: str = 'utf-8'):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.handler = logging.FileHandler(filename, mode, encoding)
        self.handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    def get_handler(self) -> logging.Handler: return self.handler

class RotatingFileHandler:
    def __init__(self, filename: str, max_bytes: int = 10*1024*1024, backup_count: int = 5, level: str = "INFO"):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.handler = logging.handlers.RotatingFileHandler(filename, maxBytes=max_bytes, backupCount=backup_count)
        self.handler.setLevel(getattr(logging, level.upper(), logging.INFO))
        self.handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    def get_handler(self) -> logging.Handler: return self.handler
