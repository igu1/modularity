# Product Module
Product management with multi-tenant support
This module provides functionality for managing products in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /product` - List all products
- `GET /product/create` - Show create form
- `POST /product/create` - Create new product
- `GET /api/product` - Get all products as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the product
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all products
- `get_by_id(id)`: Get product by ID
- `create(item)`: Create new product
- `update(id, item)`: Update existing product
- `delete(id)`: Delete product
product_module = env.get_module('product')
service = product_module.services['product_service']
items = service.get_all()
new_item = ProductModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
