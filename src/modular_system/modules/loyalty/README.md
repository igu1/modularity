# Loyalty Module
Customer loyalty and points system
This module provides functionality for managing loyaltys in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /loyalty` - List all loyaltys
- `GET /loyalty/create` - Show create form
- `POST /loyalty/create` - Create new loyalty
- `GET /api/loyalty` - Get all loyaltys as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the loyalty
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all loyaltys
- `get_by_id(id)`: Get loyalty by ID
- `create(item)`: Create new loyalty
- `update(id, item)`: Update existing loyalty
- `delete(id)`: Delete loyalty
loyalty_module = env.get_module('loyalty')
service = loyalty_module.services['loyalty_service']
items = service.get_all()
new_item = LoyaltyModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
