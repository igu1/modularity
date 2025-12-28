# Order Module
Order management and tracking
This module provides functionality for managing orders in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /order` - List all orders
- `GET /order/create` - Show create form
- `POST /order/create` - Create new order
- `GET /api/order` - Get all orders as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the order
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all orders
- `get_by_id(id)`: Get order by ID
- `create(item)`: Create new order
- `update(id, item)`: Update existing order
- `delete(id)`: Delete order
order_module = env.get_module('order')
service = order_module.services['order_service']
items = service.get_all()
new_item = OrderModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
