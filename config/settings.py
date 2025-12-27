"""Configuration management for the modular system."""

import os
import json
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    url: str = "sqlite:///modular_system.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600


@dataclass
class LoggingConfig:
    """Logging configuration settings."""
    level: str = "INFO"
    log_dir: str = "logs"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    console_output: bool = True
    file_output: bool = True


@dataclass
class ServerConfig:
    """Server configuration settings."""
    host: str = "localhost"
    port: int = 8080
    debug: bool = False
    workers: int = 1
    reload: bool = False


@dataclass
class SecurityConfig:
    """Security configuration settings."""
    secret_key: str = "your-secret-key-change-in-production"
    session_timeout: int = 3600
    csrf_protection: bool = True
    cors_enabled: bool = True
    cors_origins: list = None
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class CacheConfig:
    """Cache configuration settings."""
    type: str = "memory"  # memory, file, redis
    ttl: int = 300
    max_size: int = 1000
    file_dir: str = "cache"
    
    # Redis settings (if using Redis)
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[str] = None


@dataclass
class Config:
    """Main configuration class."""
    database: DatabaseConfig = None
    logging: LoggingConfig = None
    server: ServerConfig = None
    security: SecurityConfig = None
    cache: CacheConfig = None
    
    def __post_init__(self):
        if self.database is None:
            self.database = DatabaseConfig()
        if self.logging is None:
            self.logging = LoggingConfig()
        if self.server is None:
            self.server = ServerConfig()
        if self.security is None:
            self.security = SecurityConfig()
        if self.cache is None:
            self.cache = CacheConfig()


class ConfigManager:
    """Configuration manager for loading and managing settings."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file or self._find_config_file()
        self.config = Config()
        self._load_config()
    
    def _find_config_file(self) -> str:
        """Find configuration file in standard locations."""
        possible_locations = [
            'config.json',
            'config/config.json',
            'settings.json',
            os.path.expanduser('~/.modular_system/config.json'),
            '/etc/modular_system/config.json'
        ]
        
        for location in possible_locations:
            if os.path.exists(location):
                return location
        
        # Return default location if none found
        return 'config.json'
    
    def _load_config(self):
        """Load configuration from file and environment variables."""
        # Load from file if it exists
        if os.path.exists(self.config_file):
            self._load_from_file()
        
        # Override with environment variables
        self._load_from_environment()
    
    def _load_from_file(self):
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            
            # Update config with loaded data
            self._update_config_from_dict(data)
            
        except Exception as e:
            print(f"Warning: Could not load config file {self.config_file}: {e}")
    
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # Database settings
        if os.getenv('DATABASE_URL'):
            self.config.database.url = os.getenv('DATABASE_URL')
        if os.getenv('DATABASE_ECHO'):
            self.config.database.echo = os.getenv('DATABASE_ECHO').lower() == 'true'
        
        # Server settings
        if os.getenv('SERVER_HOST'):
            self.config.server.host = os.getenv('SERVER_HOST')
        if os.getenv('SERVER_PORT'):
            self.config.server.port = int(os.getenv('SERVER_PORT'))
        if os.getenv('SERVER_DEBUG'):
            self.config.server.debug = os.getenv('SERVER_DEBUG').lower() == 'true'
        
        # Logging settings
        if os.getenv('LOG_LEVEL'):
            self.config.logging.level = os.getenv('LOG_LEVEL')
        if os.getenv('LOG_DIR'):
            self.config.logging.log_dir = os.getenv('LOG_DIR')
        
        # Security settings
        if os.getenv('SECRET_KEY'):
            self.config.security.secret_key = os.getenv('SECRET_KEY')
        if os.getenv('CORS_ENABLED'):
            self.config.security.cors_enabled = os.getenv('CORS_ENABLED').lower() == 'true'
        
        # Cache settings
        if os.getenv('CACHE_TYPE'):
            self.config.cache.type = os.getenv('CACHE_TYPE')
        if os.getenv('CACHE_TTL'):
            self.config.cache.ttl = int(os.getenv('CACHE_TTL'))
    
    def _update_config_from_dict(self, data: Dict[str, Any]):
        """Update configuration from dictionary."""
        if 'database' in data:
            db_data = data['database']
            for key, value in db_data.items():
                if hasattr(self.config.database, key):
                    setattr(self.config.database, key, value)
        
        if 'logging' in data:
            log_data = data['logging']
            for key, value in log_data.items():
                if hasattr(self.config.logging, key):
                    setattr(self.config.logging, key, value)
        
        if 'server' in data:
            server_data = data['server']
            for key, value in server_data.items():
                if hasattr(self.config.server, key):
                    setattr(self.config.server, key, value)
        
        if 'security' in data:
            security_data = data['security']
            for key, value in security_data.items():
                if hasattr(self.config.security, key):
                    setattr(self.config.security, key, value)
        
        if 'cache' in data:
            cache_data = data['cache']
            for key, value in cache_data.items():
                if hasattr(self.config.cache, key):
                    setattr(self.config.cache, key, value)
    
    def save_config(self, file_path: Optional[str] = None):
        """
        Save current configuration to file.
        
        Args:
            file_path: Path to save configuration (uses default if None)
        """
        target_file = file_path or self.config_file
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        
        # Convert config to dictionary and save
        config_dict = asdict(self.config)
        
        with open(target_file, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def get_database_url(self) -> str:
        """Get the database URL."""
        return self.config.database.url
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.config.server.debug
    
    def get_log_level(self) -> str:
        """Get the log level."""
        return self.config.logging.level
    
    def get_server_config(self) -> ServerConfig:
        """Get server configuration."""
        return self.config.server
    
    def get_database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return self.config.database
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return self.config.logging
    
    def get_security_config(self) -> SecurityConfig:
        """Get security configuration."""
        return self.config.security
    
    def get_cache_config(self) -> CacheConfig:
        """Get cache configuration."""
        return self.config.cache
    
    def update_setting(self, section: str, key: str, value: Any):
        """
        Update a specific setting.
        
        Args:
            section: Configuration section (database, logging, etc.)
            key: Setting key
            value: New value
        """
        if hasattr(self.config, section):
            section_config = getattr(self.config, section)
            if hasattr(section_config, key):
                setattr(section_config, key, value)
            else:
                raise ValueError(f"Invalid key '{key}' for section '{section}'")
        else:
            raise ValueError(f"Invalid section '{section}'")
    
    def get_setting(self, section: str, key: str, default: Any = None) -> Any:
        """
        Get a specific setting.
        
        Args:
            section: Configuration section
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        try:
            if hasattr(self.config, section):
                section_config = getattr(self.config, section)
                if hasattr(section_config, key):
                    return getattr(section_config, key)
            return default
        except Exception:
            return default
    
    def validate_config(self) -> Dict[str, list]:
        """
        Validate configuration settings.
        
        Returns:
            Dictionary with validation errors by section
        """
        errors = {}
        
        # Validate database config
        db_errors = []
        if not self.config.database.url:
            db_errors.append("Database URL is required")
        if self.config.database.pool_size < 1:
            db_errors.append("Pool size must be at least 1")
        if db_errors:
            errors['database'] = db_errors
        
        # Validate server config
        server_errors = []
        if not self.config.server.host:
            server_errors.append("Server host is required")
        if not (1 <= self.config.server.port <= 65535):
            server_errors.append("Server port must be between 1 and 65535")
        if server_errors:
            errors['server'] = server_errors
        
        # Validate logging config
        log_errors = []
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.config.logging.level.upper() not in valid_levels:
            log_errors.append(f"Log level must be one of: {', '.join(valid_levels)}")
        if log_errors:
            errors['logging'] = log_errors
        
        # Validate security config
        security_errors = []
        if not self.config.security.secret_key or len(self.config.security.secret_key) < 16:
            security_errors.append("Secret key must be at least 16 characters long")
        if security_errors:
            errors['security'] = security_errors
        
        return errors
    
    def create_default_config_file(self, file_path: str):
        """
        Create a default configuration file.
        
        Args:
            file_path: Path where to create the config file
        """
        default_config = Config()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Convert to dictionary and save
        config_dict = asdict(default_config)
        
        with open(file_path, 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        return {
            'config_file': self.config_file,
            'database_url': self.config.database.url,
            'server_host': self.config.server.host,
            'server_port': self.config.server.port,
            'debug_mode': self.config.server.debug,
            'log_level': self.config.logging.level,
            'log_dir': self.config.logging.log_dir,
            'cache_type': self.config.cache.type,
            'cors_enabled': self.config.security.cors_enabled
        }


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config_manager.config


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance."""
    return config_manager


def reload_config(config_file: Optional[str] = None):
    """Reload configuration from file."""
    global config_manager
    config_manager = ConfigManager(config_file)


def get_database_url() -> str:
    """Get the database URL."""
    return config_manager.get_database_url()


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return config_manager.is_debug_mode()
