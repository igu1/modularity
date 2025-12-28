# Category Module
Product category management
This module provides functionality for managing categorys in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /category` - List all categorys
- `GET /category/create` - Show create form
- `POST /category/create` - Create new category
- `GET /api/category` - Get all categorys as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the category
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all categorys
- `get_by_id(id)`: Get category by ID
- `create(item)`: Create new category
- `update(id, item)`: Update existing category
- `delete(id)`: Delete category
category_module = env.get_module('category')
service = category_module.services['category_service']
items = service.get_all()
new_item = CategoryModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
