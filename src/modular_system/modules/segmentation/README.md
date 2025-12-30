# Segmentation Module
Customer segmentation and tagging
This module provides functionality for managing segmentations in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /segmentation` - List all segmentations
- `GET /segmentation/create` - Show create form
- `POST /segmentation/create` - Create new segmentation
- `GET /api/segmentation` - Get all segmentations as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the segmentation
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all segmentations
- `get_by_id(id)`: Get segmentation by ID
- `create(item)`: Create new segmentation
- `update(id, item)`: Update existing segmentation
- `delete(id)`: Delete segmentation
segmentation_module = env.get_module('segmentation')
service = segmentation_module.services['segmentation_service']
items = service.get_all()
new_item = SegmentationModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
