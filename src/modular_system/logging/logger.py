"""Enhanced logging system for the modular framework."""

import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Union
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class CoreLogger:
    """
    Centralized logging system for the modular framework.
    
    Provides module-specific logging with file rotation,
    console output, and structured log formatting.
    """
    
    def __init__(self, log_dir: str = 'logs', log_level: str = 'INFO'):
        """
        Initialize the core logger.
        
        Args:
            log_dir: Directory to store log files
            log_level: Default logging level
        """
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self._loggers: Dict[str, logging.Logger] = {}
        self._handlers: Dict[str, logging.Handler] = {}
        
        # Ensure log directory exists
        self._ensure_log_directory()
        
        # Setup root logger
        self._setup_root_logger()
        
        # Setup default handlers
        self._setup_default_handlers()
    
    def _ensure_log_directory(self):
        """Ensure log directory exists."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
    
    def _setup_root_logger(self):
        """Setup the root logger configuration."""
        logging.basicConfig(
            level=self.log_level,
            format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[]
        )
    
    def _setup_default_handlers(self):
        """Setup default console and file handlers."""
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self._handlers['console'] = console_handler
        
        # Main application file handler with rotation
        main_log_file = os.path.join(self.log_dir, 'application.log')
        file_handler = RotatingFileHandler(
            main_log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        self._handlers['file'] = file_handler
    
    def get_logger(self, module_name: str, module_class: Optional[str] = None) -> logging.Logger:
        """
        Get or create a logger for a specific module.
        
        Args:
            module_name: Name of the module
            module_class: Optional class name within the module
            
        Returns:
            Logger instance
        """
        logger_name = f"modules.{module_name}"
        if module_class:
            logger_name += f".{module_class}"
        
        if logger_name not in self._loggers:
            self._loggers[logger_name] = self._create_module_logger(logger_name, module_name)
        
        return self._loggers[logger_name]
    
    def _create_module_logger(self, logger_name: str, module_name: str) -> logging.Logger:
        """
        Create a logger for a specific module.
        
        Args:
            logger_name: Full logger name
            module_name: Module name for file naming
            
        Returns:
            Configured logger instance
        """
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)
        
        # Avoid duplicate handlers
        if logger.handlers:
            return logger
        
        # Create module-specific file handler
        log_file = os.path.join(self.log_dir, f'{module_name}_{datetime.now().strftime("%Y%m%d")}.log')
        module_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        module_handler.setLevel(self.log_level)
        
        # Detailed formatter for module logs
        module_formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s: %(message)s | '
            'File: %(filename)s:%(lineno)d | Func: %(funcName)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        module_handler.setFormatter(module_formatter)
        
        # Add handlers
        logger.addHandler(module_handler)
        logger.addHandler(self._handlers['console'])
        logger.addHandler(self._handlers['file'])
        
        # Prevent propagation to root logger to avoid duplicates
        logger.propagate = False
        
        return logger
    
    def log(self, module_name: str, message: str, level: str = 'info', 
            module_class: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        """
        Log a message with specified level.
        
        Args:
            module_name: Name of the module
            message: Log message
            level: Log level (debug, info, warning, error, critical)
            module_class: Optional class name
            extra: Extra data to include in log record
        """
        logger = self.get_logger(module_name, module_class)
        
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        
        log_level = level_map.get(level.lower(), logging.INFO)
        
        # Add extra data if provided
        log_extra = extra or {}
        
        # Log the message
        logger.log(log_level, message, extra=log_extra)
        
        # Also print important messages to console with formatting
        if level in ['error', 'critical']:
            print(f'[{module_name.upper()}] {level.upper()}: {message}', file=sys.stderr)
        elif level == 'warning':
            print(f'[{module_name.upper()}] {level.upper()}: {message}', file=sys.stderr)
        elif self.log_level <= logging.INFO:
            print(f'[{module_name.upper()}] {level.upper()}: {message}')
    
    def log_event(self, event_data: Dict[str, Any]):
        """
        Log structured event data.
        
        Args:
            event_data: Dictionary containing event information
        """
        event_name = event_data.get('event_name', 'unknown')
        source = event_data.get('source', 'unknown')
        data = event_data.get('data', {})
        timestamp = event_data.get('timestamp', datetime.now().isoformat())
        
        message = f"Event '{event_name}' from {source}"
        if data:
            message += f" | Data: {data}"
        
        self.log(source or 'system', f"EVENT: {message}", 'info')
    
    def log_request(self, method: str, path: str, status_code: int, 
                   response_time: Optional[float] = None, client_ip: str = 'unknown'):
        """
        Log HTTP request information.
        
        Args:
            method: HTTP method
            path: Request path
            status_code: Response status code
            response_time: Optional response time in milliseconds
            client_ip: Client IP address
        """
        message = f"{method} {path} - {status_code}"
        if response_time is not None:
            message += f" ({response_time:.2f}ms)"
        message += f" - {client_ip}"
        
        # Determine log level based on status code
        if status_code >= 500:
            level = 'error'
        elif status_code >= 400:
            level = 'warning'
        else:
            level = 'info'
        
        self.log('http', message, level)
    
    def log_error(self, module_name: str, message: str, exception: Optional[Exception] = None,
                  module_class: Optional[str] = None):
        """
        Log an error with optional exception details.
        
        Args:
            module_name: Name of the module
            message: Error message
            exception: Optional exception object
            module_class: Optional class name
        """
        error_msg = message
        
        if exception:
            error_msg += f" - {type(exception).__name__}: {str(exception)}"
            
            # Add traceback for debugging
            import traceback
            error_msg += f"\nTraceback: {traceback.format_exc()}"
        
        self.log(module_name, error_msg, 'error', module_class)
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
        """
        Log performance metrics.
        
        Args:
            operation: Name of the operation
            duration: Duration in seconds
            details: Optional additional details
        """
        message = f"Operation '{operation}' completed in {duration:.3f}s"
        if details:
            message += f" | Details: {details}"
        
        self.log('performance', message, 'info')
    
    def set_level(self, level: str):
        """
        Set the logging level for all loggers.
        
        Args:
            level: New logging level
        """
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        
        for logger in self._loggers.values():
            logger.setLevel(self.log_level)
        
        for handler in self._handlers.values():
            handler.setLevel(self.log_level)
    
    def add_handler(self, name: str, handler: logging.Handler):
        """
        Add a custom handler to all loggers.
        
        Args:
            name: Name for the handler
            handler: Handler instance
        """
        self._handlers[name] = handler
        
        # Add to existing loggers
        for logger in self._loggers.values():
            logger.addHandler(handler)
    
    def remove_handler(self, name: str):
        """
        Remove a handler from all loggers.
        
        Args:
            name: Name of the handler to remove
        """
        if name in self._handlers:
            handler = self._handlers[name]
            
            for logger in self._loggers.values():
                logger.removeHandler(handler)
            
            del self._handlers[name]
    
    def get_log_files(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about log files.
        
        Returns:
            Dictionary with log file information
        """
        log_files = {}
        
        try:
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(self.log_dir, filename)
                    stat = os.stat(filepath)
                    
                    log_files[filename] = {
                        'path': filepath,
                        'size': stat.st_size,
                        'size_human': self._format_file_size(stat.st_size),
                        'created': datetime.fromtimestamp(stat.st_ctime),
                        'modified': datetime.fromtimestamp(stat.st_mtime)
                    }
        except Exception as e:
            self.log('logger', f"Error getting log files: {e}", 'error')
        
        return log_files
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def cleanup_old_logs(self, days_to_keep: int = 30) -> int:
        """
        Clean up old log files.
        
        Args:
            days_to_keep: Number of days to keep log files
            
        Returns:
            Number of files deleted
        """
        deleted_count = 0
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        
        try:
            for filename in os.listdir(self.log_dir):
                if filename.endswith('.log'):
                    filepath = os.path.join(self.log_dir, filename)
                    if os.path.getmtime(filepath) < cutoff_date:
                        os.remove(filepath)
                        deleted_count += 1
                        self.log('logger', f"Deleted old log file: {filename}", 'info')
        except Exception as e:
            self.log('logger', f"Error cleaning up old logs: {e}", 'error')
        
        return deleted_count
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Dictionary with logging statistics
        """
        return {
            'total_loggers': len(self._loggers),
            'total_handlers': len(self._handlers),
            'log_level': logging.getLevelName(self.log_level),
            'log_directory': self.log_dir,
            'log_files': len(self.get_log_files())
        }


# Global logger instance
core_logger = CoreLogger()


def get_logger(module_name: str, module_class: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        module_name: Name of the module
        module_class: Optional class name
        
    Returns:
        Logger instance
    """
    return core_logger.get_logger(module_name, module_class)


def log_event(event_data: Dict[str, Any]):
    """
    Log a structured event.
    
    Args:
        event_data: Event data dictionary
    """
    core_logger.log_event(event_data)


def log_error(module_name: str, message: str, exception: Optional[Exception] = None):
    """
    Log an error message.
    
    Args:
        module_name: Name of the module
        message: Error message
        exception: Optional exception
    """
    core_logger.log_error(module_name, message, exception)


def set_log_level(level: str):
    """
    Set the global logging level.
    
    Args:
        level: Logging level
    """
    core_logger.set_level(level)
