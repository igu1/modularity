                                                     

import json
from typing import Any


class APIViews:
                                            
    
    def __init__(self, module):
\
\
\
\
\
           
        self.module = module
        self.logger = module.logger
    
    def health_api(self, environ: dict, start_response: Any, module_instance: Any):
\
\
\
\
\
\
\
\
\
\
           
        try:
                                       
            db_status = "connected"
            try:
                from modular_system.database.connection import get_engine
                engine = get_engine()
                with engine.connect() as conn:
                    conn.execute("SELECT 1")
            except Exception as e:
                db_status = "disconnected"
                self.logger.log("base", f"Database check failed: {e}", "warning")
            
            response_data = {
                "success": True,
                "status": "healthy",
                "timestamp": str(self.module.get_timestamp()),
                "database": db_status,
                "module": "base",
                "version": "1.0.0",
                "uptime": self.module.get_uptime()
            }
            
            return self._json_response(response_data, start_response)
            
        except Exception as e:
            self.logger.log("base", f"Error in health API: {e}", "error")
            error_data = {
                "success": False,
                "status": "unhealthy",
                "error": str(e)
            }
            return self._json_response(error_data, start_response, '500 Internal Server Error')
    
    def status_api(self, environ: dict, start_response: Any, module_instance: Any):
\
\
\
\
\
\
\
\
\
\
           
        try:
            status_data = self.module.get_system_status()
            
            response_data = {
                "success": True,
                "timestamp": str(self.module.get_timestamp()),
                "system": status_data,
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
            
            return self._json_response(response_data, start_response)
            
        except Exception as e:
            self.logger.log("base", f"Error in status API: {e}", "error")
            error_data = {
                "success": False,
                "error": str(e)
            }
            return self._json_response(error_data, start_response, '500 Internal Server Error')
    
    def _json_response(self, data: dict, start_response: Any, status: str = '200 OK'):
\
\
\
\
\
\
\
\
\
\
           
        body = json.dumps(data, indent=2).encode('utf-8')
        start_response(status, [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(body)))
        ])
        return [body]
