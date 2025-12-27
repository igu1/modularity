#!/usr/bin/env python3
"""
Migration script to move from old modular structure to new production-ready structure.

This script helps migrate existing modules and configurations from the old structure
to the new organized structure.
"""

import os
import shutil
import sys
from pathlib import Path


def create_backup(source_dir: str, backup_name: str):
    """Create a backup of the source directory."""
    backup_path = f"{source_dir}_{backup_name}"
    print(f"Creating backup: {backup_path}")
    
    try:
        shutil.copytree(source_dir, backup_path)
        print(f"✓ Backup created: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"✗ Failed to create backup: {e}")
        return None


def migrate_modules(old_modules_dir: str, new_modules_dir: str):
    """Migrate modules from old to new structure."""
    print(f"\nMigrating modules from {old_modules_dir} to {new_modules_dir}")
    
    if not os.path.exists(old_modules_dir):
        print(f"✗ Old modules directory not found: {old_modules_dir}")
        return False
    
    # Ensure new modules directory exists
    os.makedirs(new_modules_dir, exist_ok=True)
    
    # Copy module files
    migrated_count = 0
    for item in os.listdir(old_modules_dir):
        old_path = os.path.join(old_modules_dir, item)
        new_path = os.path.join(new_modules_dir, item)
        
        if os.path.isfile(old_path) and item.endswith('.py'):
            try:
                shutil.copy2(old_path, new_path)
                print(f"  ✓ Migrated module: {item}")
                migrated_count += 1
            except Exception as e:
                print(f"  ✗ Failed to migrate {item}: {e}")
    
    print(f"✓ Migrated {migrated_count} module files")
    return True


def migrate_patches(old_patches_dir: str, new_extensions_dir: str):
    """Migrate patches from old to new structure."""
    print(f"\nMigrating patches from {old_patches_dir} to {new_extensions_dir}")
    
    if not os.path.exists(old_patches_dir):
        print(f"✗ Old patches directory not found: {old_patches_dir}")
        return False
    
    # Ensure new extensions directory exists
    os.makedirs(new_extensions_dir, exist_ok=True)
    
    # Copy patch files
    migrated_count = 0
    for item in os.listdir(old_patches_dir):
        old_path = os.path.join(old_patches_dir, item)
        new_path = os.path.join(new_extensions_dir, item)
        
        if os.path.isfile(old_path) and item.endswith('.py'):
            try:
                shutil.copy2(old_path, new_path)
                print(f"  ✓ Migrated patch: {item}")
                migrated_count += 1
            except Exception as e:
                print(f"  ✗ Failed to migrate {item}: {e}")
    
    print(f"✓ Migrated {migrated_count} patch files")
    return True


def update_imports_in_file(file_path: str, import_mapping: dict):
    """Update imports in a Python file according to the mapping."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Update imports according to mapping
        for old_import, new_import in import_mapping.items():
            content = content.replace(old_import, new_import)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    except Exception as e:
        print(f"  ✗ Error updating {file_path}: {e}")
        return False


def update_python_imports(directory: str):
    """Update Python imports to match new structure."""
    print(f"\nUpdating imports in {directory}")
    
    import_mapping = {
        'from registry import': 'from modular_system.core import',
        'from core import': 'from modular_system.core import',
        'from database import': 'from modular_system.database import',
        'from helper import': 'from modular_system.utils import',
        'from logger import': 'from modular_system.logging import',
        'from patches import': 'from modular_system.extensions import',
        'from modules import': 'from modular_system.modules import',
        'from environment import': 'from modular_system.core import',
        'import registry': 'from modular_system.core import registry',
        'import core': 'from modular_system.core import core',
        'import database': 'from modular_system.database import database',
        'import helper': 'from modular_system.utils import helper',
        'import logger': 'from modular_system.logging import logger',
        'import patches': 'from modular_system.extensions import patches',
        'import modules': 'from modular_system.modules import modules',
    }
    
    updated_count = 0
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_imports_in_file(file_path, import_mapping):
                    print(f"  ✓ Updated imports: {file}")
                    updated_count += 1
    
    print(f"✓ Updated imports in {updated_count} files")


def create_new_config(old_config_path: str, new_config_path: str):
    """Create new configuration file based on old settings."""
    print(f"\nCreating configuration file: {new_config_path}")
    
    # Default new configuration
    new_config = {
        "database": {
            "url": "sqlite:///modular_system.db",
            "echo": False,
            "pool_size": 5,
            "max_overflow": 10
        },
        "server": {
            "host": "localhost",
            "port": 8080,
            "debug": False
        },
        "logging": {
            "level": "INFO",
            "log_dir": "logs",
            "console_output": True,
            "file_output": True
        },
        "security": {
            "secret_key": "your-secret-key-change-in-production",
            "cors_enabled": True
        },
        "cache": {
            "type": "memory",
            "ttl": 300,
            "max_size": 1000
        }
    }
    
    try:
        import json
        os.makedirs(os.path.dirname(new_config_path), exist_ok=True)
        with open(new_config_path, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2)
        print(f"✓ Configuration file created: {new_config_path}")
        return True
    except Exception as e:
        print(f"✗ Failed to create configuration: {e}")
        return False


def create_migration_summary():
    """Create a summary of migration changes."""
    summary = """
# Migration Summary

## What Changed

### 1. Package Structure
- Old: Flat structure with files in root directory
- New: Organized package structure under `src/modular_system/`

### 2. Module Organization
- `core.py` → `src/modular_system/core/application.py`
- `registry.py` → `src/modular_system/core/registry.py`
- `environment.py` → `src/modular_system/core/environment.py`
- `database.py` → `src/modular_system/database/connection.py`
- `helper.py` → Split into multiple utility modules
- `logger.py` → `src/modular_system/logging/logger.py`
- `patches/` → `src/modular_system/extensions/`

### 3. New Components
- Configuration management system
- Enhanced database layer with repository pattern
- Comprehensive utility libraries
- Improved logging system
- Web layer with routing and middleware

### 4. Import Changes
Update your imports from:
```python
from registry import Registry
from database import init_db
from helper import WSGIHelpers
```

To:
```python
from modular_system.core import Registry
from modular_system.database import init_db
from modular_system.utils import WSGIHelpers
```

## Next Steps

1. Update your application entry point to use `app.py`
2. Review and update configuration in `config/settings.py`
3. Test your modules with the new structure
4. Update any custom import statements
5. Run tests to ensure everything works

## Benefits

- Better code organization and maintainability
- Separation of concerns
- Easier testing and debugging
- Production-ready features
- Comprehensive documentation
- Standard Python packaging

## Getting Help

- Check the README.md for detailed documentation
- Review the new API in the source code
- Run the test suite to understand usage patterns
- Check the migration guide for specific changes
"""
    
    try:
        with open('MIGRATION_SUMMARY.md', 'w', encoding='utf-8') as f:
            f.write(summary)
        print("✓ Migration summary created: MIGRATION_SUMMARY.md")
        return True
    except Exception as e:
        print(f"✗ Failed to create migration summary: {e}")
        return False


def main():
    """Main migration function."""
    print("=== Modular System Migration Tool ===")
    print("This tool will migrate your old modular system to the new production-ready structure.\n")
    
    # Define paths
    old_base = "/home/ez/tmp/modular"
    new_base = "/home/ez/tmp/modular_system"
    
    if not os.path.exists(old_base):
        print(f"✗ Old modular system directory not found: {old_base}")
        sys.exit(1)
    
    if not os.path.exists(new_base):
        print(f"✗ New modular system directory not found: {new_base}")
        print("Please ensure the new structure is created first.")
        sys.exit(1)
    
    # Create backup
    backup_path = create_backup(old_base, "backup_before_migration")
    if not backup_path:
        print("✗ Migration aborted due to backup failure.")
        sys.exit(1)
    
    print(f"\n✓ Backup created at: {backup_path}")
    
    # Perform migration steps
    success = True
    
    # 1. Migrate modules
    old_modules = os.path.join(old_base, "modules")
    new_modules = os.path.join(new_base, "src/modular_system/modules")
    if not migrate_modules(old_modules, new_modules):
        success = False
    
    # 2. Migrate patches
    old_patches = os.path.join(old_base, "patches")
    new_extensions = os.path.join(new_base, "src/modular_system/extensions")
    if not migrate_patches(old_patches, new_extensions):
        success = False
    
    # 3. Update imports in migrated files
    if os.path.exists(new_modules):
        update_python_imports(new_modules)
    if os.path.exists(new_extensions):
        update_python_imports(new_extensions)
    
    # 4. Create configuration file
    config_path = os.path.join(new_base, "config.json")
    create_new_config("", config_path)
    
    # 5. Create migration summary
    create_migration_summary()
    
    # Final summary
    print("\n=== Migration Complete ===")
    if success:
        print("✓ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Review the migrated code in the new structure")
        print("2. Update your application to use the new entry point (app.py)")
        print("3. Test your modules with the new imports")
        print("4. Read MIGRATION_SUMMARY.md for detailed changes")
    else:
        print("⚠ Migration completed with some issues.")
        print("Please review the output above and fix any problems.")
    
    print(f"\nBackup location: {backup_path}")
    print("Keep the backup until you've verified the migration works correctly.")


if __name__ == "__main__":
    main()
