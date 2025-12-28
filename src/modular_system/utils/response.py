import json
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, Optional, Union, List
from ..logging.logger import CoreLogger
logger = CoreLogger()
class WSGIHelpers:
    STATUS_CODES = {
        200: 'OK',
        201: 'Created',
        204: 'No Content',
        301: 'Moved Permanently',
        302: 'Found',
        304: 'Not Modified',
        400: 'Bad Request',
        401: 'Unauthorized',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        409: 'Conflict',
        422: 'Unprocessable Entity',
        500: 'Internal Server Error',
        502: 'Bad Gateway',
        503: 'Service Unavailable'
    }
    @staticmethod
    def response(start_response, data: Union[str, Dict, Any], 
                 status_code: int = 200, content_type: str = "application/json",
                 headers: Optional[List[tuple]] = None) -> List[bytes]:
        if isinstance(data, (dict, list)):
            response_data = json.dumps(data, default=str).encode('utf-8')
            if content_type == "application/json":
                content_type = "application/json; charset=utf-8"
        else:
            response_data = str(data).encode('utf-8')
            if content_type == "application/json":
                content_type = "text/plain; charset=utf-8"
        response_headers = [
            ('Content-Type', content_type),
            ('Content-Length', str(len(response_data))),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'),
            ('Access-Control-Max-Age', '86400')
        ]
        if headers:
            response_headers.extend(headers)
        status_text = WSGIHelpers.STATUS_CODES.get(status_code, 'Unknown')
        status_line = f"{status_code} {status_text}"
        start_response(status_line, response_headers)
        return [response_data]
    @staticmethod
    def json_response(start_response, data: Dict[str, Any], status_code: int = 200) -> List[bytes]:
        return WSGIHelpers.response(start_response, data, status_code, "application/json")
    @staticmethod
    def html_response(start_response, html: str, status_code: int = 200) -> List[bytes]:
        return WSGIHelpers.response(start_response, html, status_code, "text/html")
    @staticmethod
    def text_response(start_response, text: str, status_code: int = 200) -> List[bytes]:
        return WSGIHelpers.response(start_response, text, status_code, "text/plain")
    @staticmethod
    def error_response(start_response, message: str, status_code: int = 400, 
                      error_code: Optional[str] = None) -> List[bytes]:
        error_data = {
            'error': True,
            'message': message,
            'status_code': status_code
        }
        if error_code:
            error_data['error_code'] = error_code
        return WSGIHelpers.json_response(start_response, error_data, status_code)
    @staticmethod
    def success_response(start_response, data: Any = None, message: str = "Success") -> List[bytes]:
        response_data = {
            'success': True,
            'message': message
        }
        if data is not None:
            response_data['data'] = data
        return WSGIHelpers.json_response(start_response, response_data)
    @staticmethod
    def pagination_response(start_response, items: List[Any], total: int, 
                           page: int, per_page: int, **kwargs) -> List[bytes]:
        pages = (total + per_page - 1) // per_page
        pagination_data = {
            'items': items,
            'pagination': {
                'total': total,
                'page': page,
                'per_page': per_page,
                'pages': pages,
                'has_next': page < pages,
                'has_prev': page > 1,
                **kwargs
            }
        }
        return WSGIHelpers.json_response(start_response, pagination_data)
    @staticmethod
    def redirect_response(start_response, location: str, status_code: int = 302) -> List[bytes]:
        headers = [('Location', location)]
        return WSGIHelpers.response(start_response, '', status_code, 'text/plain', headers)
    @staticmethod
    def file_response(start_response, file_path: str, content_type: Optional[str] = None,
                     download_name: Optional[str] = None) -> List[bytes]:
        try:
            from ..utils.file_ops import FileHelpers
            if not FileHelpers.file_exists(file_path):
                return WSGIHelpers.error_response(start_response, "File not found", 404)
            if not content_type:
                content_type = FileHelpers.get_mime_type(file_path)
            with open(file_path, 'rb') as f:
                file_content = f.read()
            headers = []
            if download_name:
                headers.append(('Content-Disposition', f'attachment; filename="{download_name}"'))
            return WSGIHelpers.response(start_response, file_content, 200, content_type, headers)
        except Exception as e:
            logger.log("wsgi", f"Error serving file {file_path}: {e}", "error")
            return WSGIHelpers.error_response(start_response, "Error serving file", 500)
    @staticmethod
    def get_body(environ: dict) -> Optional[Dict[str, Any]]:
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
        except (ValueError, TypeError):
            content_length = 0
        if content_length > 0:
            try:
                body_bytes = environ["wsgi.input"].read(content_length)
                body_text = body_bytes.decode("utf-8")
                if not body_text.strip():
                    return {}
                try:
                    return json.loads(body_text)
                except json.JSONDecodeError as e:
                    logger.log("wsgi", f"JSON decode error: {e}", "error")
                    logger.log("wsgi", f"Body text: '{body_text}'", "error")
                    return None
            except Exception as e:
                logger.log("wsgi", f"Error reading request body: {e}", "error")
                return None
        return {}
    @staticmethod
    def get_params(environ: dict) -> Dict[str, str]:
        query_string = environ.get("QUERY_STRING", "")
        params = parse_qs(query_string)
        result = {}
        for key, value in params.items():
            result[key] = value[0] if len(value) == 1 else value
        return result
    @staticmethod
    def get_path_info(environ: dict) -> str:
        return environ.get('PATH_INFO', '/')
    @staticmethod
    def get_method(environ: dict) -> str:
        return environ.get('REQUEST_METHOD', 'GET')
    @staticmethod
    def get_headers(environ: dict) -> Dict[str, str]:
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        if 'CONTENT_TYPE' in environ:
            headers['Content-Type'] = environ['CONTENT_TYPE']
        if 'CONTENT_LENGTH' in environ:
            headers['Content-Length'] = environ['CONTENT_LENGTH']
        return headers
    @staticmethod
    def get_client_ip(environ: dict) -> str:
        forwarded_for = environ.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        real_ip = environ.get('HTTP_X_REAL_IP')
        if real_ip:
            return real_ip
        return environ.get('REMOTE_ADDR', 'unknown')
    @staticmethod
    def get_user_agent(environ: dict) -> str:
        return environ.get('HTTP_USER_AGENT', 'unknown')
    @staticmethod
    def get_referer(environ: dict) -> Optional[str]:
        return environ.get('HTTP_REFERER')
    @staticmethod
    def parse_content_type(environ: dict) -> Dict[str, str]:
        content_type = environ.get('CONTENT_TYPE', '')
        if not content_type:
            return {'type': '', 'charset': ''}
        parts = [part.strip() for part in content_type.split(';')]
        result = {'type': parts[0]}
        for part in parts[1:]:
            if part.startswith('charset='):
                result['charset'] = part[8:].strip('"')
        return result
    @staticmethod
    def is_json_request(environ: dict) -> bool:
        content_type_info = WSGIHelpers.parse_content_type(environ)
        return content_type_info.get('type', '').startswith('application/json')
    @staticmethod
    def is_ajax_request(environ: dict) -> bool:
        return environ.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    @staticmethod
    def get_request_info(environ: dict) -> Dict[str, Any]:
        return {
            'method': WSGIHelpers.get_method(environ),
            'path': WSGIHelpers.get_path_info(environ),
            'query_params': WSGIHelpers.get_params(environ),
            'headers': WSGIHelpers.get_headers(environ),
            'client_ip': WSGIHelpers.get_client_ip(environ),
            'user_agent': WSGIHelpers.get_user_agent(environ),
            'referer': WSGIHelpers.get_referer(environ),
            'content_type': WSGIHelpers.parse_content_type(environ),
            'is_json': WSGIHelpers.is_json_request(environ),
            'is_ajax': WSGIHelpers.is_ajax_request(environ)
        }
class Request:
    def __init__(self, environ: dict):
        self.environ = environ
        self._body = None
        self._params = None
        self._headers = None
        self._json = None
    @property
    def method(self) -> str:
        return WSGIHelpers.get_method(self.environ)
    @property
    def path(self) -> str:
        return WSGIHelpers.get_path_info(self.environ)
    @property
    def params(self) -> Dict[str, str]:
        if self._params is None:
            self._params = WSGIHelpers.get_params(self.environ)
        return self._params
    @property
    def headers(self) -> Dict[str, str]:
        if self._headers is None:
            self._headers = WSGIHelpers.get_headers(self.environ)
        return self._headers
    @property
    def body(self) -> Optional[Dict[str, Any]]:
        if self._json is None:
            self._json = WSGIHelpers.get_body(self.environ)
        return self._json
    @property
    def client_ip(self) -> str:
        return WSGIHelpers.get_client_ip(self.environ)
    @property
    def user_agent(self) -> str:
        return WSGIHelpers.get_user_agent(self.environ)
    def get_param(self, name: str, default: Any = None) -> Any:
        return self.params.get(name, default)
    def get_header(self, name: str, default: Any = None) -> Any:
        return self.headers.get(name, default)
    def get_body_field(self, name: str, default: Any = None) -> Any:
        if self.body:
            return self.body.get(name, default)
        return default
    def is_method(self, method: str) -> bool:
        return self.method.upper() == method.upper()
    def is_get(self) -> bool:
        return self.is_method('GET')
    def is_post(self) -> bool:
        return self.is_method('POST')
    def is_put(self) -> bool:
        return self.is_method('PUT')
    def is_delete(self) -> bool:
        return self.is_method('DELETE')
    def is_ajax(self) -> bool:
        return WSGIHelpers.is_ajax_request(self.environ)
    def is_json(self) -> bool:
        return WSGIHelpers.is_json_request(self.environ)
