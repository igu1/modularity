# Base Module

## Overview

The Base module provides the foundational functionality for the Modular System. It serves as the core module that all other modules depend on, providing database connections, system monitoring, health checks, and core utilities.

## Features

- ✅ Database connection management
- ✅ System health monitoring
- ✅ Beautiful home page with module overview
- ✅ Health check endpoints
- ✅ System status API
- ✅ Error handling and logging
- ✅ Module registry integration

## Structure

```
base/
├── __init__.py              # Module entry point (BaseModule class)
├── README.md                # This file
│
├── models/                  # Data models
│   ├── __init__.py
│   └── base_model.py       # BaseModel with common functionality
│
├── views/                   # View handlers
│   ├── __init__.py
│   ├── web.py              # HTML views (home, health, status)
│   └── api.py              # JSON API views
│
├── routes/                  # URL routing
│   ├── __init__.py
│   ├── web.py              # Web routes
│   └── api.py              # API routes
│
└── services/                # Business logic
    ├── __init__.py
    └── system_service.py   # System monitoring and health checks
```

## Database Schema

The base module doesn't create specific tables but provides the database
connection infrastructure that other modules use.

## Endpoints

### Web Routes (HTML)
- `GET /` - Beautiful home page with module overview
- `GET /health` - Health check page
- `GET /status` - System status page

### API Routes (JSON)
- `GET /api/health` - Health check API
- `GET /api/status` - System status API

## Usage

### Home Page
The home page provides a beautiful overview of all loaded modules with:
- System status dashboard
- Module cards with descriptions
- Quick access links to each module
- Visual health indicators

### Health Check
The health check endpoints provide:
- Database connection status
- Module loading status
- Memory usage information
- Overall system health

### System Status
Detailed system information including:
- Loaded modules count
- Total routes count
- Extensions count
- Database status
- Uptime information

## Models

### BaseModel

Base class for all database entities providing:
- Common fields (id, created_at, updated_at)
- Serialization methods (to_dict, from_dict, from_db_row)
- Validation framework
- Type safety with type hints

## Services

### SystemService

Business logic for system operations:
- `get_system_status()` - Comprehensive system status
- `check_health()` - Health check with multiple checks
- `_check_database_status()` - Database connectivity
- `_check_modules_status()` - Module loading status
- `_check_memory_status()` - Memory usage monitoring

## Dependencies

- No dependencies (base module)

## API Examples

### Health Check
```bash
curl http://localhost:8080/api/health
```

Response:
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-12-27 16:30:00",
  "database": "connected",
  "module": "base",
  "version": "1.0.0",
  "uptime": "5m 30s"
}
```

### System Status
```bash
curl http://localhost:8080/api/status
```

Response:
```json
{
  "success": true,
  "timestamp": "2025-12-27 16:30:00",
  "system": {
    "loaded_modules": 3,
    "modules": ["base", "contacts", "products"],
    "total_routes": 20,
    "extensions": 7,
    "database": "connected",
    "uptime": "5m 30s"
  },
  "modules": {
    "base": {"status": "active", "version": "1.0.0"},
    "contacts": {"status": "active", "version": "1.0.0"},
    "products": {"status": "active", "version": "1.0.0"}
  },
  "database": {
    "status": "connected",
    "type": "sqlite",
    "url": "sqlite:///modular_system.db"
  }
}
```

## Integration

The base module is automatically loaded first and provides:
- Database connection for all modules
- System monitoring capabilities
- Core web endpoints
- Logging infrastructure

Other modules should depend on the base module for:
- Database access
- Logging functionality
- System status integration

## Configuration

The base module accepts configuration for:
- Database connection settings
- Logging preferences
- Health check intervals

Example:
```python
config = {
    'database': {
        'url': 'sqlite:///modular_system.db'
    },
    'logging': {
        'level': 'INFO'
    }
}

base_module = BaseModule(config)
```

## Testing

Run tests:
```bash
python -m pytest src/modular_system/modules/base/tests/
```

## License

MIT License
