import sys
import os
from typing import Dict, Any
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from modular_system import ModularSystem
from config.settings import get_config_manager, is_debug_mode
def main() -> None:
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
    default_modules = [
        'base',
        'product', 
        'organization', 
        # 'category', 
        # 'cart',
        # 'wishlist',
        # 'checkout',
        # 'order'
    ]
    for module_name in default_modules:
        try:
            if system.load_module(module_name):
                print(f"✓ Loaded module: {module_name}")
            else:
                print(f"✗ Failed to load module: {module_name}")
                sys.exit(1)
        except Exception as e:
            print(f"✗ Error loading module {module_name}: {e}")
            sys.exit(1)
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
