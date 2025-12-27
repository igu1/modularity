                                                        

import logging
import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Union
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler


class CoreLogger:
\
\
\
\
\
       
    
    def __init__(self, log_dir: str = 'logs', log_level: str = 'INFO'):
\
\
\
\
\
\
           
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self._loggers: Dict[str, logging.Logger] = {}
        self._handlers: Dict[str, logging.Handler] = {}
        
                                     
        self._ensure_log_directory()
        
                           
        self._setup_root_logger()
        
                                
        self._setup_default_handlers()
    
    def _ensure_log_directory(self):
                                          
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir, exist_ok=True)
    
    def _setup_root_logger(self):
                                                  
        logging.basicConfig(
            level=self.log_level,
            format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[]
        )
    
    def _setup_default_handlers(self):
                                                      
                         
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self._handlers['console'] = console_handler
        
                                                     
        main_log_file = os.path.join(self.log_dir, 'application.log')
        file_handler = RotatingFileHandler(
            main_log_file,
            maxBytes=10 * 1024 * 1024,        
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
\
\
\
\
\
\
\
\
\
           
        logger_name = f"modules.{module_name}"
        if module_class:
            logger_name += f".{module_class}"
        
        if logger_name not in self._loggers:
            self._loggers[logger_name] = self._create_module_logger(logger_name, module_name)
        
        return self._loggers[logger_name]
    
    def _create_module_logger(self, logger_name: str, module_name: str) -> logging.Logger:
\
\
\
\
\
\
\
\
\
           
        logger = logging.getLogger(logger_name)
        logger.setLevel(self.log_level)
        
                                  
        if logger.handlers:
            return logger
        
                                             
        log_file = os.path.join(self.log_dir, f'{module_name}_{datetime.now().strftime("%Y%m%d")}.log')
        module_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,       
            backupCount=3,
            encoding='utf-8'
        )
        module_handler.setLevel(self.log_level)
        
                                            
        module_formatter = logging.Formatter(
            '[%(asctime)s] %(name)s - %(levelname)s: %(message)s | '
            'File: %(filename)s:%(lineno)d | Func: %(funcName)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        module_handler.setFormatter(module_formatter)
        
                      
        logger.addHandler(module_handler)
        logger.addHandler(self._handlers['console'])
        logger.addHandler(self._handlers['file'])
        
                                                                
        logger.propagate = False
        
        return logger
    
    def log(self, module_name: str, message: str, level: str = 'info', 
            module_class: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
\
\
\
\
\
\
\
\
\
           
        logger = self.get_logger(module_name, module_class)
        
        level_map = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'critical': logging.CRITICAL
        }
        
        log_level = level_map.get(level.lower(), logging.INFO)
        
                                    
        log_extra = extra or {}
        
                         
        logger.log(log_level, message, extra=log_extra)
        
                                                                  
        if level in ['error', 'critical']:
            print(f'[{module_name.upper()}] {level.upper()}: {message}', file=sys.stderr)
        elif level == 'warning':
            print(f'[{module_name.upper()}] {level.upper()}: {message}', file=sys.stderr)
        elif self.log_level <= logging.INFO:
            print(f'[{module_name.upper()}] {level.upper()}: {message}')
    
    def log_event(self, event_data: Dict[str, Any]):
\
\
\
\
\
           
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
\
\
\
\
\
\
\
\
\
           
        message = f"{method} {path} - {status_code}"
        if response_time is not None:
            message += f" ({response_time:.2f}ms)"
        message += f" - {client_ip}"
        
                                                  
        if status_code >= 500:
            level = 'error'
        elif status_code >= 400:
            level = 'warning'
        else:
            level = 'info'
        
        self.log('http', message, level)
    
    def log_error(self, module_name: str, message: str, exception: Optional[Exception] = None,
                  module_class: Optional[str] = None):
\
\
\
\
\
\
\
\
           
        error_msg = message
        
        if exception:
            error_msg += f" - {type(exception).__name__}: {str(exception)}"
            
                                         
            import traceback
            error_msg += f"\nTraceback: {traceback.format_exc()}"
        
        self.log(module_name, error_msg, 'error', module_class)
    
    def log_performance(self, operation: str, duration: float, details: Optional[Dict[str, Any]] = None):
\
\
\
\
\
\
\
           
        message = f"Operation '{operation}' completed in {duration:.3f}s"
        if details:
            message += f" | Details: {details}"
        
        self.log('performance', message, 'info')
    
    def set_level(self, level: str):
\
\
\
\
\
           
        self.log_level = getattr(logging, level.upper(), logging.INFO)
        
        for logger in self._loggers.values():
            logger.setLevel(self.log_level)
        
        for handler in self._handlers.values():
            handler.setLevel(self.log_level)
    
    def add_handler(self, name: str, handler: logging.Handler):
\
\
\
\
\
\
           
        self._handlers[name] = handler
        
                                 
        for logger in self._loggers.values():
            logger.addHandler(handler)
    
    def remove_handler(self, name: str):
\
\
\
\
\
           
        if name in self._handlers:
            handler = self._handlers[name]
            
            for logger in self._loggers.values():
                logger.removeHandler(handler)
            
            del self._handlers[name]
    
    def get_log_files(self) -> Dict[str, Dict[str, Any]]:
\
\
\
\
\
           
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
                                                        
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def cleanup_old_logs(self, days_to_keep: int = 30) -> int:
\
\
\
\
\
\
\
\
           
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
\
\
\
\
\
           
        return {
            'total_loggers': len(self._loggers),
            'total_handlers': len(self._handlers),
            'log_level': logging.getLevelName(self.log_level),
            'log_directory': self.log_dir,
            'log_files': len(self.get_log_files())
        }


                        
core_logger = CoreLogger()


def get_logger(module_name: str, module_class: Optional[str] = None) -> logging.Logger:
\
\
\
\
\
\
\
\
\
       
    return core_logger.get_logger(module_name, module_class)


def log_event(event_data: Dict[str, Any]):
\
\
\
\
\
       
    core_logger.log_event(event_data)


def log_error(module_name: str, message: str, exception: Optional[Exception] = None):
\
\
\
\
\
\
\
       
    core_logger.log_error(module_name, message, exception)


def set_log_level(level: str):
\
\
\
\
\
       
    core_logger.set_level(level)
