"""Modules package for the modular system."""

import os
import importlib

# Available modules dictionary
modules = {}


def discover_modules():
    """
    Discover available modules in the modules directory.
    
    Returns:
        Dictionary mapping module names to module classes
    """
    modules_dir = os.path.dirname(__file__)
    available = {}
    
    for item in os.listdir(modules_dir):
        item_path = os.path.join(modules_dir, item)
        if os.path.isdir(item_path) and not item.startswith('__'):
            try:
                # Import the module
                module = importlib.import_module(f'.{item}', package='modular_system.modules')
                
                # Look for a module class (e.g., BaseModule)
                module_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type) and attr_name.endswith('Module'):
                        module_class = attr
                        break
                
                if module_class:
                    available[item] = module_class
            except Exception as e:
                print(f"Warning: Could not load module {item}: {e}")
    
    return available


# Initialize available modules
modules = discover_modules()
