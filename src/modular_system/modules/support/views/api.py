from typing import Any
import json
from modular_system.modules.base.utils.auth_decorator import require_auth

class APIViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger

    @require_auth
    def list_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            service = self.module.services['support_service']
            items = service.get_all()
            data = {
                'success': True,
                'module': 'support',
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
            self.logger.log("support", f"Error in list API: {e}", "error")
            error_data = {'success': False, 'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]

    @require_auth
    def user_tickets_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            user_id = params.get('user_id')
            service = self.module.services['support_service']
            tickets = service.get_user_tickets(user_id)
            data = {'success': True, 'tickets': [t.to_dict() for t in tickets]}
            response_body = json.dumps(data).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))])
            return [response_body]
        except Exception as e:
            error_data = {'success': False, 'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]

    @require_auth
    def create_ticket_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            data = json.loads(environ['wsgi.input'].read(content_length))
            service = self.module.services['support_service']
            # Use authenticated user_id from token
            user_id = environ.get('user_id')
            ticket_id = service.create_ticket(
                user_id,
                data.get('subject'),
                data.get('message'),
                data.get('priority', 'medium')
            )
            res = {'success': bool(ticket_id), 'ticket_id': ticket_id}
            response_body = json.dumps(res).encode('utf-8')
            start_response('201 Created' if ticket_id else '400 Bad Request', [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))])
            return [response_body]
        except Exception as e:
            error_data = {'success': False, 'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
