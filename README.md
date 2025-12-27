# Modular System

A flexible, modular Python framework with inter-module communication capabilities.

## Features

- **Modular Architecture**: Clean separation of concerns with standardized module structure
- **Event-Driven Communication**: Publish/Subscribe messaging system
- **Module Access**: Direct inter-module communication
- **Database Integration**: SQLAlchemy-based data persistence
- **Beautiful Web Interface**: Modern, responsive UI
- **API Endpoints**: RESTful JSON APIs

## Quick Start

1. **Setup Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```bash
   python app.py
   ```

3. **Access the Application**
   - Open http://localhost:8080 in your browser
   - API available at http://localhost:8080/api/

## Base Module

The system includes the **base module** which provides:
- Core system functionality
- Database connections
- Health monitoring
- System status APIs
- Beautiful home page

## Architecture

```
Modular System/
├── src/modular_system/
│   ├── core/           # Core framework
│   ├── database/       # Database layer
│   ├── messaging/      # Pub/Sub system
│   ├── logging/        # Logging system
│   └── modules/
│       └── base/       # Base module (included)
├── app.py              # Application entry point
├── config.py           # Configuration
├── requirements.txt    # Dependencies
└── .gitignore          # Git ignore rules
```

## License

MIT License
