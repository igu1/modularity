import sys
import os
import json
import tempfile
import io

# Add src to sys.path
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from modular_system.core.application import ModularSystem
from modular_system.database.connection import init_db

def debug_load():
    db_fd, db_path = tempfile.mkstemp()
    db_url = f"sqlite:///{db_path}"
    
    config = {
        'database': {'url': db_url}
    }
    
    print(f"DEBUG: Initializing ModularSystem with config: {config}")
    system = ModularSystem(config)
    
    print(f"DEBUG: Initializing DB: {db_url}")
    init_db(db_url)
    
    from modular_system.modules import modules as available_modules
    print(f"DEBUG: Available modules keys: {list(available_modules.keys())}")
    system.registry.set_available_modules(available_modules)
    
    print(f"DEBUG: Loading 'base' module...")
    success = system.load_module('base')
    print(f"DEBUG: 'base' load success: {success}")
    
    if not success:
        # The registry should have logged the error. 
        # Since we are running in a script, it should print to stdout.
        pass

    if success:
        print(f"DEBUG: Testing OrganizationService.create...")
        org_service = system.env.get_service('organization_service')
        if org_service:
            from modular_system.modules.base.models.organization import OrganizationModel
            new_org = OrganizationModel(name="Test", slug="test")
            try:
                org_id = org_service.create(new_org)
                print(f"DEBUG: Created Org ID: {org_id}")
            except Exception as e:
                print(f"DEBUG: Create Org Failed: {e}")
                import traceback
                traceback.print_exc()
        else:
            print("DEBUG: organization_service not found")

    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

if __name__ == "__main__":
    debug_load()
