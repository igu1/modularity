# Review Module
Product reviews and ratings
This module provides functionality for managing reviews in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /review` - List all reviews
- `GET /review/create` - Show create form
- `POST /review/create` - Create new review
- `GET /api/review` - Get all reviews as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the review
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all reviews
- `get_by_id(id)`: Get review by ID
- `create(item)`: Create new review
- `update(id, item)`: Update existing review
- `delete(id)`: Delete review
review_module = env.get_module('review')
service = review_module.services['review_service']
items = service.get_all()
new_item = ReviewModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
