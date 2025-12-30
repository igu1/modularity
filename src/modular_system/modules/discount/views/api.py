from typing import Any
import json
class APIViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            service = self.module.services['discount_service']
            items = service.get_all()
            data = {
                'success': True,
                'module': 'discount',
                'data': [item.to_dict() for item in items],
                'total': len(items)
            }
            response_body = json.dumps(data, indent=2).encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("discount", f"Error in list API: {e}", "error")
            error_data = {'success': False, 'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def validate_coupon_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            post_data = environ['wsgi.input'].read(content_length)
            data = json.loads(post_data)
            
            service = self.module.services['discount_service']
            result = service.validate_coupon(data.get('code'), data.get('total', 0))
            
            response_body = json.dumps(result).encode('utf-8')
            status = '200 OK' if result.get('success') else '400 Bad Request'
            start_response(status, [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("discount", f"Error in validate API: {e}", "error")
            error_data = {'success': False, 'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
