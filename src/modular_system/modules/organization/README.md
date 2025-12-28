# Organization Module
Multi-organization management for SaaS
This module provides functionality for managing organizations in the modular system.
- Feature 1
- Feature 2
- Feature 3
- `GET /organization` - List all organizations
- `GET /organization/create` - Show create form
- `POST /organization/create` - Create new organization
- `GET /api/organization` - Get all organizations as JSON
- `id` (Integer): Primary key
- `name` (String): Name of the organization
- `description` (Text): Description
- `is_active` (Boolean): Active status
- `created_at` (DateTime): Creation timestamp
- `updated_at` (DateTime): Last update timestamp
- `get_all()`: Get all organizations
- `get_by_id(id)`: Get organization by ID
- `create(item)`: Create new organization
- `update(id, item)`: Update existing organization
- `delete(id)`: Delete organization
organization_module = env.get_module('organization')
service = organization_module.services['organization_service']
items = service.get_all()
new_item = OrganizationModel(name="Test", description="Test item")
item_id = service.create(new_item)
```
- base module
Modular System Team
1.0.0
