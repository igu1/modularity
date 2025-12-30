from typing import Any
import json
class APIViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            service = self.module.services['analytics_service']
            items = service.get_all()
            data = {
                'success': True,
                'module': 'analytics',
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
            self.logger.log("analytics", f"Error in list API: {e}", "error")
            error_data = {'success': False, 'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def track_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            data = json.loads(environ['wsgi.input'].read(content_length))
            service = self.module.services['analytics_service']
            success = service.track_event(
                data.get('event_type'),
                data.get('user_id'),
                data.get('path'),
                data.get('metadata')
            )
            res = {'success': success}
            response_body = json.dumps(res).encode('utf-8')
            start_response('201 Created' if success else '400 Bad Request', [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))])
            return [response_body]
        except Exception as e:
            return [json.dumps({'success': False, 'error': str(e)}).encode('utf-8')]

    def stats_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            service = self.module.services['analytics_service']
            stats = service.get_stats()
            data = {'success': True, 'stats': stats}
            response_body = json.dumps(data).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))])
            return [response_body]
        except Exception as e:
            return [json.dumps({'success': False, 'error': str(e)}).encode('utf-8')]
