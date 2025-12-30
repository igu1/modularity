# Discount Module
Discount and coupon management system
This module provides functionality for managing discounts in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /discount` - List all discounts
- `GET /discount/create` - Show create form
- `POST /discount/create` - Create new discount
- `GET /api/discount` - Get all discounts as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the discount
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all discounts
- `get_by_id(id)`: Get discount by ID
- `create(item)`: Create new discount
- `update(id, item)`: Update existing discount
- `delete(id)`: Delete discount
discount_module = env.get_module('discount')
service = discount_module.services['discount_service']
items = service.get_all()
new_item = DiscountModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
