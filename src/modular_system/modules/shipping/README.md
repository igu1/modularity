# Shipping Module
Shipping methods and tracking
This module provides functionality for managing shippings in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /shipping` - List all shippings
- `GET /shipping/create` - Show create form
- `POST /shipping/create` - Create new shipping
- `GET /api/shipping` - Get all shippings as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the shipping
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all shippings
- `get_by_id(id)`: Get shipping by ID
- `create(item)`: Create new shipping
- `update(id, item)`: Update existing shipping
- `delete(id)`: Delete shipping
shipping_module = env.get_module('shipping')
service = shipping_module.services['shipping_service']
items = service.get_all()
new_item = ShippingModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
