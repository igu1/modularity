"""
Main entry point for the modular system application.

This module provides the primary entry point for running the modular system.
It handles configuration loading, module initialization, and server startup.

Only the base module is loaded by default, which provides core functionality
including database connections and basic web endpoints.

Usage:
    python app.py

The application will:
    1. Load configuration from config.json or environment variables
    2. Validate the configuration
    3. Initialize the modular system
    4. Load the base module
    5. Start the web server

Environment Variables:
    DATABASE_URL: Database connection string
    SERVER_HOST: Server host address (default: localhost)
    SERVER_PORT: Server port (default: 8080)
    SERVER_DEBUG: Enable debug mode (default: False)
    LOG_LEVEL: Logging level (default: INFO)
    SECRET_KEY: Secret key for security
"""

import sys
import os
from typing import Dict, Any

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from modular_system import ModularSystem
from config.settings import get_config_manager, is_debug_mode


def main() -> None:
    """
    Main entry point for the application.
    
    This function orchestrates the entire application startup process:
    1. Loads and validates configuration
    2. Initializes the modular system
    3. Loads the base module
    4. Starts the web server
    
    Raises:
        SystemExit: If configuration validation fails or server encounters an error
    """
    config_manager = get_config_manager()
    config = config_manager.config
    
    errors = config_manager.validate_config()
    if errors:
        print("Configuration errors found:")
        for section, section_errors in errors.items():
            print(f"  {section}:")
            for error in section_errors:
                print(f"    - {error}")
        sys.exit(1)
    
    system = ModularSystem(config.__dict__)
    
    default_modules = ['base']
    for module_name in default_modules:
        try:
            if system.load_module(module_name):
                print(f"✓ Loaded module: {module_name}")
            else:
                print(f"✗ Failed to load module: {module_name}")
                sys.exit(1)  # Exit if base module fails to load
        except Exception as e:
            print(f"✗ Error loading module {module_name}: {e}")
            sys.exit(1)  # Exit if base module fails to load
    
    system.load_manifest()
    
    status = system.get_status()
    print(f"\nSystem Status:")
    print(f"  Loaded modules: {status['registry']['loaded_modules']}")
    print(f"  Services: {status['registry']['services']}")
    print(f"  Routes: {status['registry']['routes']}")
    print(f"  Extensions: {status['extensions']['total_patches']}")
    
    print(f"\nStarting server on {config.server.host}:{config.server.port}")
    print(f"Debug mode: {config.server.debug}")
    print(f"Log level: {config.logging.level}")
    print(f"Database: {config.database.url}")
    
    try:
        system.run(
            host=config.server.host,
            port=config.server.port,
            debug=config.server.debug
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
