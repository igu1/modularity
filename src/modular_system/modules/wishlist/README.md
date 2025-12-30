# Wishlist Module
Product wishlist management
This module provides functionality for managing wishlists in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /wishlist` - List all wishlists
- `GET /wishlist/create` - Show create form
- `POST /wishlist/create` - Create new wishlist
- `GET /api/wishlist` - Get all wishlists as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the wishlist
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all wishlists
- `get_by_id(id)`: Get wishlist by ID
- `create(item)`: Create new wishlist
- `update(id, item)`: Update existing wishlist
- `delete(id)`: Delete wishlist
wishlist_module = env.get_module('wishlist')
service = wishlist_module.services['wishlist_service']
items = service.get_all()
new_item = WishlistModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
