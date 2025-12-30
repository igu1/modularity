# Support Module
Customer support ticketing system
This module provides functionality for managing supports in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /support` - List all supports
- `GET /support/create` - Show create form
- `POST /support/create` - Create new support
- `GET /api/support` - Get all supports as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the support
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all supports
- `get_by_id(id)`: Get support by ID
- `create(item)`: Create new support
- `update(id, item)`: Update existing support
- `delete(id)`: Delete support
support_module = env.get_module('support')
service = support_module.services['support_service']
items = service.get_all()
new_item = SupportModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
