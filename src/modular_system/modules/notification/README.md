# Notification Module
In-app notification system
This module provides functionality for managing notifications in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /notification` - List all notifications
- `GET /notification/create` - Show create form
- `POST /notification/create` - Create new notification
- `GET /api/notification` - Get all notifications as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the notification
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all notifications
- `get_by_id(id)`: Get notification by ID
- `create(item)`: Create new notification
- `update(id, item)`: Update existing notification
- `delete(id)`: Delete notification
notification_module = env.get_module('notification')
service = notification_module.services['notification_service']
items = service.get_all()
new_item = NotificationModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
