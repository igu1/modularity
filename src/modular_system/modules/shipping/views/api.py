from typing import Any
import json
class APIViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            service = self.module.services['shipping_service']
            items = service.get_all()
            data = {
                'success': True,
                'module': 'shipping',
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
            self.logger.log("shipping", f"Error in list API: {e}", "error")
            error_data = {'success': False, 'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def methods_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            service = self.module.services['shipping_service']
            methods = service.get_active_methods()
            data = {'success': True, 'methods': [m.to_dict() for m in methods]}
            response_body = json.dumps(data).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))])
            return [response_body]
        except Exception as e:
            return [json.dumps({'success': False, 'error': str(e)}).encode('utf-8')]

    def update_tracking_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            data = json.loads(environ['wsgi.input'].read(content_length))
            service = self.module.services['shipping_service']
            success = service.update_tracking(
                data.get('order_id'),
                data.get('carrier'),
                data.get('tracking_number'),
                data.get('status', 'shipped')
            )
            res = {'success': success}
            response_body = json.dumps(res).encode('utf-8')
            start_response('200 OK' if success else '400 Bad Request', [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))])
            return [response_body]
        except Exception as e:
            return [json.dumps({'success': False, 'error': str(e)}).encode('utf-8')]
