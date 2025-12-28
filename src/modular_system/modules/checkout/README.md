# Checkout Module
Checkout process and payment integration
This module provides functionality for managing checkouts in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /checkout` - List all checkouts
- `GET /checkout/create` - Show create form
- `POST /checkout/create` - Create new checkout
- `GET /api/checkout` - Get all checkouts as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the checkout
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all checkouts
- `get_by_id(id)`: Get checkout by ID
- `create(item)`: Create new checkout
- `update(id, item)`: Update existing checkout
- `delete(id)`: Delete checkout
checkout_module = env.get_module('checkout')
service = checkout_module.services['checkout_service']
items = service.get_all()
new_item = CheckoutModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
