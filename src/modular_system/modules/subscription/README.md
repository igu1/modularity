# Subscription Module
Recurring subscription management
This module provides functionality for managing subscriptions in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /subscription` - List all subscriptions
- `GET /subscription/create` - Show create form
- `POST /subscription/create` - Create new subscription
- `GET /api/subscription` - Get all subscriptions as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the subscription
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all subscriptions
- `get_by_id(id)`: Get subscription by ID
- `create(item)`: Create new subscription
- `update(id, item)`: Update existing subscription
- `delete(id)`: Delete subscription
subscription_module = env.get_module('subscription')
service = subscription_module.services['subscription_service']
items = service.get_all()
new_item = SubscriptionModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
