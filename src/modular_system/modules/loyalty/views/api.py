from typing import Any
import json
class APIViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            service = self.module.services['loyalty_service']
            items = service.get_all()
            data = {
                'success': True,
                'module': 'loyalty',
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
            self.logger.log("loyalty", f"Error in list API: {e}", "error")
            error_data = {'success': False, 'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def get_points_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            user_id = params.get('user_id')
            service = self.module.services['loyalty_service']
            points = service.get_points(user_id)
            data = {'success': True, 'user_id': user_id, 'points': points}
            response_body = json.dumps(data).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))])
            return [response_body]
        except Exception as e:
            self.logger.log("loyalty", f"Error in points API: {e}", "error")
            return [json.dumps({'success': False, 'error': str(e)}).encode('utf-8')]

    def add_points_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            data = json.loads(environ['wsgi.input'].read(content_length))
            service = self.module.services['loyalty_service']
            success = service.add_points(data.get('user_id'), data.get('points', 0), data.get('reason', 'Purchase'))
            res = {'success': success}
            response_body = json.dumps(res).encode('utf-8')
            start_response('200 OK' if success else '400 Bad Request', [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))])
            return [response_body]
        except Exception as e:
            self.logger.log("loyalty", f"Error in add points API: {e}", "error")
            return [json.dumps({'success': False, 'error': str(e)}).encode('utf-8')]
