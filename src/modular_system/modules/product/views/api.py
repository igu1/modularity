import json
from typing import Any
from ..models.product import ProductModel

class APIViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger

    def list_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            org = environ.get('ORG_CONTEXT')
            org_id = org.id if org else None
            
            product_service = self.module.services.get('product_service')
            products = product_service.get_all(organization_id=org_id)
            
            return self._json_response([p.to_dict() for p in products], start_response)
        except Exception as e:
            return self._json_error(str(e), start_response)

    def get_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            product_id = int(params.get('id', 0))
            
            product_service = self.module.services.get('product_service')
            product = product_service.get_by_id(product_id)
            
            if not product:
                return self._json_error("Product not found", start_response, '404 Not Found')
            
            # Multi-tenancy check
            org = environ.get('ORG_CONTEXT')
            if org and product.organization_id != org.id:
                return self._json_error("Unauthorized", start_response, '403 Forbidden')
                
            return self._json_response(product.to_dict(), start_response)
        except Exception as e:
            return self._json_error(str(e), start_response)

    def create_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            body = environ['wsgi.input'].read(content_length)
            data = json.loads(body)
            
            org = environ.get('ORG_CONTEXT')
            if org:
                data['organization_id'] = org.id
            elif 'organization_id' not in data:
                return self._json_error("Organization ID required", start_response, '400 Bad Request')

            product = ProductModel.from_dict(data)
            product_service = self.module.services.get('product_service')
            product_id = product_service.create(product)
            
            if product_id:
                return self._json_response({"id": product_id, "message": "Product created"}, start_response, '201 Created')
            return self._json_error("Failed to create product", start_response)
        except Exception as e:
            return self._json_error(str(e), start_response)

    def update_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            product_id = int(params.get('id', 0))
            
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            body = environ['wsgi.input'].read(content_length)
            data = json.loads(body)
            
            product_service = self.module.services.get('product_service')
            existing = product_service.get_by_id(product_id)
            if not existing:
                return self._json_error("Product not found", start_response, '404 Not Found')
                
            org = environ.get('ORG_CONTEXT')
            if org and existing.organization_id != org.id:
                return self._json_error("Unauthorized", start_response, '403 Forbidden')

            updated_product = ProductModel.from_dict(data)
            # Ensure org_id doesn't change if in org context
            if org:
                updated_product.organization_id = org.id

            if product_service.update(product_id, updated_product):
                return self._json_response({"message": "Product updated"}, start_response)
            return self._json_error("Failed to update product", start_response)
        except Exception as e:
            return self._json_error(str(e), start_response)

    def delete_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            product_id = int(params.get('id', 0))
            
            product_service = self.module.services.get('product_service')
            existing = product_service.get_by_id(product_id)
            if not existing:
                return self._json_error("Product not found", start_response, '404 Not Found')
                
            org = environ.get('ORG_CONTEXT')
            if org and existing.organization_id != org.id:
                return self._json_error("Unauthorized", start_response, '403 Forbidden')

            if product_service.delete(product_id):
                return self._json_response({"message": "Product deleted"}, start_response)
            return self._json_error("Failed to delete product", start_response)
        except Exception as e:
            return self._json_error(str(e), start_response)

    def _json_response(self, data: Any, start_response: Any, status: str = '200 OK'):
        body = json.dumps(data, indent=2).encode('utf-8')
        start_response(status, [
            ('Content-Type', 'application/json'),
            ('Content-Length', str(len(body)))
        ])
        return [body]

    def _json_error(self, message: str, start_response: Any, status: str = '500 Internal Server Error'):
        return self._json_response({"success": False, "error": message}, start_response, status)
