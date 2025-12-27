"""Logging handlers for the modular system."""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional, TextIO


class ConsoleHandler:
    """
    Console logging handler that outputs to stdout/stderr.
    
    Provides formatted console output with support for different log levels
    and customizable formatting.
    """
    
    def __init__(self, stream: Optional[TextIO] = None, level: str = "INFO"):
        """
        Initialize console handler.
        
        Args:
            stream: Output stream (defaults to sys.stdout)
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.stream = stream or sys.stdout
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.handler = logging.StreamHandler(self.stream)
        self.handler.setLevel(self.level)
        
        # Set formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.handler.setFormatter(formatter)
    
    def get_handler(self) -> logging.Handler:
        """
        Get the underlying logging handler.
        
        Returns:
            Configured logging handler instance
        """
        return self.handler


class FileHandler:
    """
    File logging handler for writing logs to files.
    
    Provides file-based logging with support for log rotation
    and customizable file paths.
    """
    
    def __init__(self, filename: str, level: str = "INFO", 
                 mode: str = 'a', encoding: str = 'utf-8'):
        """
        Initialize file handler.
        
        Args:
            filename: Path to log file
            level: Logging level
            mode: File open mode
            encoding: File encoding
        """
        self.filename = filename
        self.level = getattr(logging, level.upper(), logging.INFO)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        self.handler = logging.FileHandler(filename, mode, encoding)
        self.handler.setLevel(self.level)
        
        # Set formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.handler.setFormatter(formatter)
    
    def get_handler(self) -> logging.Handler:
        """
        Get the underlying logging handler.
        
        Returns:
            Configured logging handler instance
        """
        return self.handler


class RotatingFileHandler:
    """
    Rotating file logging handler with size limits.
    
    Provides automatic log rotation when files reach a maximum size,
    with support for keeping a specified number of backup files.
    """
    
    def __init__(self, filename: str, max_bytes: int = 10*1024*1024, 
                 backup_count: int = 5, level: str = "INFO"):
        """
        Initialize rotating file handler.
        
        Args:
            filename: Path to log file
            max_bytes: Maximum file size before rotation (default: 10MB)
            backup_count: Number of backup files to keep
            level: Logging level
        """
        self.filename = filename
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.level = getattr(logging, level.upper(), logging.INFO)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        self.handler = logging.handlers.RotatingFileHandler(
            filename, maxBytes=max_bytes, backupCount=backup_count
        )
        self.handler.setLevel(self.level)
        
        # Set formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.handler.setFormatter(formatter)
    
    def get_handler(self) -> logging.Handler:
        """
        Get the underlying logging handler.
        
        Returns:
            Configured logging handler instance
        """
        return self.handler
