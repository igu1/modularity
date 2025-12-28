# Cart Module
Shopping cart functionality
This module provides functionality for managing carts in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /cart` - List all carts
- `GET /cart/create` - Show create form
- `POST /cart/create` - Create new cart
- `GET /api/cart` - Get all carts as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the cart
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all carts
- `get_by_id(id)`: Get cart by ID
- `create(item)`: Create new cart
- `update(id, item)`: Update existing cart
- `delete(id)`: Delete cart
cart_module = env.get_module('cart')
service = cart_module.services['cart_service']
items = service.get_all()
new_item = CartModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
