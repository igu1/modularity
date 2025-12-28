import os
import sys
import argparse
from datetime import datetime
def create_module_structure(module_name, author="Modular System Team", description=""):
    base_path = "src/modular_system/modules"
    module_path = os.path.join(base_path, module_name)
    if os.path.exists(module_path):
        print(f"❌ Module '{module_name}' already exists at {module_path}")
        return False
    print(f"🚀 Creating module: {module_name}")
    directories = [
        "models",
        "views", 
        "routes",
        "services",
        "static",
        "templates",
        "migrations",
        "tests",
        "patches",
        "utils"
    ]
    print("✅ Creating folder structure...")
    for directory in directories:
        dir_path = os.path.join(module_path, directory)
        os.makedirs(dir_path, exist_ok=True)
        init_file = os.path.join(dir_path, "__init__.py")
        with open(init_file, 'w') as f:
            if directory == "views":
                f.write("from .web import WebViews\nfrom .api import APIViews\n\n__all__ = ['WebViews', 'APIViews']\n")
            elif directory == "services":
                service_name = f"{module_name}_service"
                class_name = f"{module_name.title().replace('_', '')}Service"
                f.write(f"from .{service_name} import {class_name}\n\n__all__ = ['{class_name}']\n")
            elif directory == "routes":
                f.write("from .web import get_routes\n\n__all__ = ['get_routes']\n")
            elif directory == "models":
                model_name = module_name
                class_name = f"{module_name.title().replace('_', '')}Model"
                f.write(f"from .{model_name} import {class_name}\n\n__all__ = ['{class_name}']\n")
            else:
                f.write("")
    print("✅ Creating module entry point...")
    create_module_init(module_path, module_name, author, description)
    print("✅ Creating model template...")
    create_model_template(module_path, module_name)
    print("✅ Creating view templates...")
    create_view_templates(module_path, module_name)
    print("✅ Creating route templates...")
    create_route_templates(module_path, module_name)
    print("✅ Creating service template...")
    create_service_template(module_path, module_name)
    print("✅ Creating README template...")
    create_readme_template(module_path, module_name, author, description)
    print(f"🎉 Module '{module_name}' created successfully!")
    print(f"📍 Location: {module_path}")
    print(f"📝 Next steps:")
    print(f"   1. Add '{module_name}' to default_modules in app.py")
    print(f"   2. Implement your module logic in the created files")
    print(f"   3. Test the module by running: python app.py")
    return True
def create_module_init(module_path, module_name, author, description):
    class_name = f"{module_name.title().replace('_', '')}Module"
    content = f'''from typing import Dict, Any, List, Optional
class {class_name}:
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {{}}
        self.name = '{module_name}'
        self.version = '1.0.0'
        self._dependencies = ['base']
        self.env = None
        from modular_system.logging.logger import CoreLogger
        self.logger = CoreLogger()
        self.web_views = None
        self.api_views = None
        self.services = None
        self.logger.log("{module_name}", "{module_name} module initialized", "info")
    @property
    def dependencies(self) -> List[str]:
        return self._dependencies
    def initialize(self, env):
        self.env = env
        self._create_table()
        from .views import WebViews, APIViews
        from .services import {module_name.title().replace('_', '')}Service
        self.web_views = WebViews(self)
        self.api_views = APIViews(self)
        self.services = {{'{module_name}_service': {module_name.title().replace('_', '')}Service(self)}}
        from .routes import get_routes
        routes = get_routes(self)
        for route_pattern, method, handler in routes:
            if hasattr(env, '_registry'):
                env._registry.add_routes([(route_pattern, method, handler)], '{module_name}')
        self.logger.log("{module_name}", "{module_name} module initialized with environment", "info")
    def _create_table(self):
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS {module_name}s (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
            with engine.connect() as conn:
                conn.execute(text(create_table_sql))
                conn.commit()
            self.logger.log("{module_name}", f"Created table: {module_name}s", "info")
        except Exception as e:
            self.logger.log("{module_name}", f"Error creating table: {{e}}", "error")
    def get_routes(self):
        from .routes import get_routes
        return get_routes(self)
    def get_info(self) -> Dict[str, Any]:
        return {{
            'name': self.name,
            'version': self.version,
            'description': '{description}',
            'author': '{author}',
            'dependencies': self._dependencies,
            'provides': ['{module_name}_feature1', '{module_name}_feature2'],
            'endpoints': {{
                '/{module_name}': 'GET - Main {module_name} page',
                '/{module_name}/create': 'GET/POST - Create new item',
                '/{module_name}/<id>': 'GET - View item details',
                '/api/{module_name}': 'GET - API endpoint (JSON)'
            }},
            'features': [
                'Feature 1',
                'Feature 2',
                'Feature 3'
            ]
        }}
    def cleanup(self):
        try:
            self.logger.log("{module_name}", "{module_name} module cleanup completed", "info")
        except Exception as e:
            self.logger.log("{module_name}", f"Error during cleanup: {{e}}", "error")
__version__ = "1.0.0"
__author__ = "{author}"
__description__ = "{description}"
'''
    init_file = os.path.join(module_path, "__init__.py")
    with open(init_file, 'w') as f:
        f.write(content)
def create_model_template(module_path, module_name):
    model_name = module_name.title().replace('_', '')
    content = f'''from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from modular_system.database.models import DatabaseModel
class {model_name}Model(DatabaseModel):
    __tablename__ = '{module_name}s'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    def validate(self) -> tuple[bool, list]:
        errors = []
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Name is required")
        return len(errors) == 0, errors
    def to_dict(self) -> Dict[str, Any]:
        return {{
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }}
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> '{model_name}Model':
        return cls(
            name=data.get('name', ''),
            description=data.get('description', ''),
            is_active=data.get('is_active', True)
        )
    @classmethod
    def from_db_row(cls, row) -> '{model_name}Model':
        return cls(
            id=row[0] if len(row) > 0 else None,
            name=row[1] if len(row) > 1 else '',
            description=row[2] if len(row) > 2 else '',
            is_active=row[3] if len(row) > 3 else True,
            created_at=row[4] if len(row) > 4 else None,
            updated_at=row[5] if len(row) > 5 else None
        )
    def update_timestamp(self):
        self.updated_at = datetime.now()
    def __repr__(self) -> str:
        return f"<{model_name}(id={{self.id}}, name='{{self.name}}')>"
'''
    model_file = os.path.join(module_path, "models", f"{module_name}.py")
    with open(model_file, 'w') as f:
        f.write(content)
def create_view_templates(module_path, module_name):
    class_name = module_name.title().replace('_', '')
    web_content = f'''from typing import Any
class WebViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>{class_name} Management</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        h1 {{ color: #333; }}
        .btn {{ padding: 10px 20px; background: #667eea; color: white; text-decoration: none; border-radius: 4px; }}
        .item {{ border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 {class_name} Management</h1>
        <p>This is the {module_name} module following the standardized structure.</p>
        <a href="/{module_name}/create" class="btn">+ Create New</a>
        <div class="item">
            <h3>Sample {class_name}</h3>
            <p>This is a sample item. Replace with your actual data.</p>
        </div>
    </div>
</body>
</html>
"""
            response_body = html.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("{module_name}", f"Error in list view: {{e}}", "error")
            error_body = f"Error: {{str(e)}}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def create_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>Create {class_name}</title>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; }}
        .form-group {{ margin-bottom: 20px; }}
        label {{ display: block; margin-bottom: 5px; font-weight: 600; color: #333; }}
        input, textarea {{ width: 100%; padding: 12px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px; }}
        .btn {{ padding: 12px 24px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>➕ Create New {class_name}</h1>
        <form method="POST">
            <div class="form-group">
                <label>Name *</label>
                <input type="text" name="name" required>
            </div>
            <div class="form-group">
                <label>Description</label>
                <textarea name="description" placeholder="Enter description..."></textarea>
            </div>
            <button type="submit" class="btn">Create {class_name}</button>
            <a href="/{module_name}" class="btn" style="background: #6c757d; text-decoration: none; display: inline-block; margin-left: 10px;">Cancel</a>
        </form>
    </div>
</body>
</html>
"""
            response_body = html.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("{module_name}", f"Error in create view: {{e}}", "error")
            error_body = f"Error: {{str(e)}}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
'''
    web_file = os.path.join(module_path, "views", "web.py")
    with open(web_file, 'w') as f:
        f.write(web_content)
    api_content = f'''from typing import Any
import json
class APIViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            data = {{
                'module': '{module_name}',
                'message': '{class_name} API endpoint',
                'data': [],
                'total': 0
            }}
            response_body = json.dumps(data, indent=2).encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("{module_name}", f"Error in list API: {{e}}", "error")
            error_data = {{'error': str(e)}}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
'''
    api_file = os.path.join(module_path, "views", "api.py")
    with open(api_file, 'w') as f:
        f.write(api_content)
def create_route_templates(module_path, module_name):
    route_content = f'''def get_routes(module):
    routes = [
        ('/{module_name}', 'GET', module.web_views.list_view),
        ('/{module_name}/create', 'GET', module.web_views.create_view),
        ('/{module_name}/create', 'POST', module.web_views.create_view),
        ('/api/{module_name}', 'GET', module.api_views.list_api),
    ]
    return routes
'''
    web_route_file = os.path.join(module_path, "routes", "web.py")
    with open(web_route_file, 'w') as f:
        f.write(route_content)
    api_route_file = os.path.join(module_path, "routes", "api.py")
    with open(api_route_file, 'w') as f:
        f.write(route_content)
def create_service_template(module_path, module_name):
    class_name = module_name.title().replace('_', '')
    service_content = f'''from typing import List, Optional, Dict, Any
from ..models.{module_name} import {class_name}Model
class {module_name.title().replace('_', '')}Service:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def get_all(self) -> List[{class_name}Model]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {module_name}s ORDER BY name"))
                items = [{class_name}Model.from_db_row(row) for row in result.fetchall()]
            self.logger.log("{module_name}", f"Retrieved {{len(items)}} items", "info")
            return items
        except Exception as e:
            self.logger.log("{module_name}", f"Error getting all items: {{e}}", "error")
            return []
    def get_by_id(self, item_id: int) -> Optional[{class_name}Model]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT * FROM {module_name}s WHERE id = :id"), {{'id': item_id}})
                row = result.fetchone()
                if row:
                    item = {class_name}Model.from_db_row(row)
                    self.logger.log("{module_name}", f"Retrieved item by ID: {{item_id}}", "info")
                    return item
            return None
        except Exception as e:
            self.logger.log("{module_name}", f"Error getting item by ID: {{e}}", "error")
            return None
    def create(self, item: {class_name}Model) -> Optional[int]:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("{module_name}", f"Validation errors: {{errors}}", "warning")
                return None
            with engine.connect() as conn:
                result = conn.execute(text(f"""
                    INSERT INTO {module_name}s (name, description, is_active)
                    VALUES (:name, :description, :is_active)
                """), {{
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                }})
                conn.commit()
                self.logger.log("{module_name}", f"Created item: {{item.name}}", "info")
                return result.lastrowid
        except Exception as e:
            self.logger.log("{module_name}", f"Error creating item: {{e}}", "error")
            return None
    def update(self, item_id: int, item: {class_name}Model) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            is_valid, errors = item.validate()
            if not is_valid:
                self.logger.log("{module_name}", f"Validation errors: {{errors}}", "warning")
                return False
            with engine.connect() as conn:
                conn.execute(text(f"""
                    UPDATE {module_name}s 
                    SET name = :name, description = :description, is_active = :is_active,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = :id
                """), {{
                    'id': item_id,
                    'name': item.name,
                    'description': item.description,
                    'is_active': item.is_active
                }})
                conn.commit()
                self.logger.log("{module_name}", f"Updated item ID: {{item_id}}", "info")
                return True
        except Exception as e:
            self.logger.log("{module_name}", f"Error updating item: {{e}}", "error")
            return False
    def delete(self, item_id: int) -> bool:
        try:
            from modular_system.database.connection import get_engine
            from sqlalchemy import text
            engine = get_engine()
            with engine.connect() as conn:
                conn.execute(text(f"DELETE FROM {module_name}s WHERE id = :id"), {{'id': item_id}})
                conn.commit()
                self.logger.log("{module_name}", f"Deleted item ID: {{item_id}}", "info")
                return True
        except Exception as e:
            self.logger.log("{module_name}", f"Error deleting item: {{e}}", "error")
            return False
'''
    service_file = os.path.join(module_path, "services", f"{module_name}_service.py")
    with open(service_file, 'w') as f:
        f.write(service_content)
def create_readme_template(module_path, module_name, author, description):
    content = f'''# {module_name.title().replace('_', '')} Module
{description}
This module provides functionality for managing {module_name}s in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /{module_name}` - List all {module_name}s
- `GET /{module_name}/create` - Show create form
- `POST /{module_name}/create` - Create new {module_name}
- `GET /api/{module_name}` - Get all {module_name}s as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the {module_name}
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all {module_name}s
- `get_by_id(id)`: Get {module_name} by ID
- `create(item)`: Create new {module_name}
- `update(id, item)`: Update existing {module_name}
- `delete(id)`: Delete {module_name}
{module_name}_module = env.get_module('{module_name}')
service = {module_name}_module.services['{module_name}_service']
items = service.get_all()
new_item = {module_name.title().replace('_', '')}Model(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
{author}
1.0.0
'''
    readme_file = os.path.join(module_path, "README.md")
    with open(readme_file, 'w') as f:
        f.write(content)
def main():
    parser = argparse.ArgumentParser(description="Create a new module for the modular system")
    parser.add_argument("name", help="Name of the module to create")
    parser.add_argument("--author", default="Modular System Team", help="Author of the module")
    parser.add_argument("--description", default="", help="Description of the module")
    args = parser.parse_args()
    if not args.name.isidentifier() or not args.name.replace('_', '').isalnum():
        print("❌ Invalid module name. Use letters, numbers, and underscores only.")
        sys.exit(1)
    success = create_module_structure(args.name, args.author, args.description)
    if success:
        print(f"\n🎯 Don't forget to:")
        print(f"   1. Add '{args.name}' to default_modules in app.py")
        print(f"   2. Implement your business logic")
        print(f"   3. Test your module: python app.py")
    else:
        sys.exit(1)
if __name__ == "__main__":
    main()
