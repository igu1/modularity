import json
from typing import Any
from ..models.organization import OrganizationModel

class APIViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger

    def organization_list(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            org_service = self.module.services.get('organization_service')
            orgs = org_service.get_all()
            return self._json_response([org.to_dict() for org in orgs], start_response)
        except Exception as e:
            return self._json_error(str(e), start_response)

    def organization_get(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            org_id = int(params.get('id', 0))
            org_service = self.module.services.get('organization_service')
            org = org_service.get_by_id(org_id)
            if not org:
                return self._json_error("Organization not found", start_response, '404 Not Found')
            return self._json_response(org.to_dict(), start_response)
        except Exception as e:
            return self._json_error(str(e), start_response)

    def organization_create(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            body = environ['wsgi.input'].read(content_length)
            data = json.loads(body)
            org = OrganizationModel.from_dict(data)
            org_service = self.module.services.get('organization_service')
            org_id = org_service.create(org)
            if org_id:
                return self._json_response({"id": org_id, "message": "Organization created"}, start_response, '201 Created')
            return self._json_error("Failed to create organization", start_response)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return self._json_error(str(e), start_response)

    def organization_update(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            org_id = int(params.get('id', 0))
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            body = environ['wsgi.input'].read(content_length)
            data = json.loads(body)
            org = OrganizationModel.from_dict(data)
            org_service = self.module.services.get('organization_service')
            if org_service.update(org_id, org):
                return self._json_response({"message": "Organization updated"}, start_response)
            return self._json_error("Failed to update organization", start_response)
        except Exception as e:
            return self._json_error(str(e), start_response)

    def organization_delete(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            org_id = int(params.get('id', 0))
            org_service = self.module.services.get('organization_service')
            if org_service.delete(org_id):
                return self._json_response({"message": "Organization deleted"}, start_response)
            return self._json_error("Failed to delete organization", start_response)
        except Exception as e:
            return self._json_error(str(e), start_response)

    def _json_error(self, message: str, start_response: Any, status: str = '500 Internal Server Error'):
        return self._json_response({"success": False, "error": message}, start_response, status)

    def health_api(self, environ: dict, start_response: Any, module_instance: Any):
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
        body = json.dumps(data, indent=2).encode('utf-8')
        start_response(status, [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(body)))
        ])
        return [body]
