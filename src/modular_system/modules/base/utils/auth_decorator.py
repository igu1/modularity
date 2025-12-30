import functools
import json
from typing import Callable

def require_auth(view_func: Callable):
    @functools.wraps(view_func)
    def wrapper(self, environ, start_response, module_instance):
        auth_header = environ.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            body = json.dumps({"success": False, "error": "Authorization required"}).encode()
            start_response('401 Unauthorized', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
            return [body]

        token = auth_header.split(' ')[1]
        base_module = module_instance.get_module('base')
        auth_service = base_module.services.get('auth_service')
        
        user_id = auth_service.verify_token(token)
        if not user_id:
            body = json.dumps({"success": False, "error": "Invalid or expired token"}).encode()
            start_response('401 Unauthorized', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
            return [body]

        environ['user_id'] = user_id
        return view_func(self, environ, start_response, module_instance)
    return wrapper
