"""WSGI response and request utilities."""

import json
from urllib.parse import parse_qs, urlparse
from typing import Dict, Any, Optional, Union, List
from ..logging.logger import CoreLogger

logger = CoreLogger()


class WSGIHelpers:
    """WSGI utility functions for handling requests and responses."""
    
    # HTTP status codes
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
        """
        Create a WSGI response.
        
        Args:
            start_response: WSGI start_response callable
            data: Response data
            status_code: HTTP status code
            content_type: Response content type
            headers: Additional headers
            
        Returns:
            Response body as list of bytes
        """
        # Prepare response data
        if isinstance(data, (dict, list)):
            response_data = json.dumps(data, default=str).encode('utf-8')
            if content_type == "application/json":
                content_type = "application/json; charset=utf-8"
        else:
            response_data = str(data).encode('utf-8')
            if content_type == "application/json":
                content_type = "text/plain; charset=utf-8"
        
        # Prepare headers
        response_headers = [
            ('Content-Type', content_type),
            ('Content-Length', str(len(response_data))),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'),
            ('Access-Control-Max-Age', '86400')
        ]
        
        # Add custom headers
        if headers:
            response_headers.extend(headers)
        
        # Get status text
        status_text = WSGIHelpers.STATUS_CODES.get(status_code, 'Unknown')
        status_line = f"{status_code} {status_text}"
        
        # Start response
        start_response(status_line, response_headers)
        
        return [response_data]
    
    @staticmethod
    def json_response(start_response, data: Dict[str, Any], status_code: int = 200) -> List[bytes]:
        """
        Create a JSON response.
        
        Args:
            start_response: WSGI start_response callable
            data: Dictionary to convert to JSON
            status_code: HTTP status code
            
        Returns:
            Response body as list of bytes
        """
        return WSGIHelpers.response(start_response, data, status_code, "application/json")
    
    @staticmethod
    def html_response(start_response, html: str, status_code: int = 200) -> List[bytes]:
        """
        Create an HTML response.
        
        Args:
            start_response: WSGI start_response callable
            html: HTML content
            status_code: HTTP status code
            
        Returns:
            Response body as list of bytes
        """
        return WSGIHelpers.response(start_response, html, status_code, "text/html")
    
    @staticmethod
    def text_response(start_response, text: str, status_code: int = 200) -> List[bytes]:
        """
        Create a plain text response.
        
        Args:
            start_response: WSGI start_response callable
            text: Text content
            status_code: HTTP status code
            
        Returns:
            Response body as list of bytes
        """
        return WSGIHelpers.response(start_response, text, status_code, "text/plain")
    
    @staticmethod
    def error_response(start_response, message: str, status_code: int = 400, 
                      error_code: Optional[str] = None) -> List[bytes]:
        """
        Create an error response.
        
        Args:
            start_response: WSGI start_response callable
            message: Error message
            status_code: HTTP status code
            error_code: Optional error code
            
        Returns:
            Response body as list of bytes
        """
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
        """
        Create a success response.
        
        Args:
            start_response: WSGI start_response callable
            data: Optional data to include
            message: Success message
            
        Returns:
            Response body as list of bytes
        """
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
        """
        Create a paginated response.
        
        Args:
            start_response: WSGI start_response callable
            items: List of items for current page
            total: Total number of items
            page: Current page number
            per_page: Items per page
            **kwargs: Additional pagination data
            
        Returns:
            Response body as list of bytes
        """
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
        """
        Create a redirect response.
        
        Args:
            start_response: WSGI start_response callable
            location: URL to redirect to
            status_code: HTTP status code (should be 3xx)
            
        Returns:
            Response body as list of bytes
        """
        headers = [('Location', location)]
        return WSGIHelpers.response(start_response, '', status_code, 'text/plain', headers)
    
    @staticmethod
    def file_response(start_response, file_path: str, content_type: Optional[str] = None,
                     download_name: Optional[str] = None) -> List[bytes]:
        """
        Create a file response.
        
        Args:
            start_response: WSGI start_response callable
            file_path: Path to the file
            content_type: Optional content type
            download_name: Optional download filename
            
        Returns:
            Response body as list of bytes
        """
        try:
            from ..utils.file_ops import FileHelpers
            
            if not FileHelpers.file_exists(file_path):
                return WSGIHelpers.error_response(start_response, "File not found", 404)
            
            # Determine content type
            if not content_type:
                content_type = FileHelpers.get_mime_type(file_path)
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # Prepare headers
            headers = []
            if download_name:
                headers.append(('Content-Disposition', f'attachment; filename="{download_name}"'))
            
            return WSGIHelpers.response(start_response, file_content, 200, content_type, headers)
            
        except Exception as e:
            logger.log("wsgi", f"Error serving file {file_path}: {e}", "error")
            return WSGIHelpers.error_response(start_response, "Error serving file", 500)
    
    # Request parsing methods
    @staticmethod
    def get_body(environ: dict) -> Optional[Dict[str, Any]]:
        """
        Extract and parse JSON body from WSGI environ.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            Parsed body as dictionary or None if error
        """
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
        """
        Extract query parameters from WSGI environ.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            Dictionary of query parameters
        """
        query_string = environ.get("QUERY_STRING", "")
        params = parse_qs(query_string)
        
        # Convert single-value lists to strings
        result = {}
        for key, value in params.items():
            result[key] = value[0] if len(value) == 1 else value
        
        return result
    
    @staticmethod
    def get_path_info(environ: dict) -> str:
        """
        Get the path info from WSGI environ.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            Path info string
        """
        return environ.get('PATH_INFO', '/')
    
    @staticmethod
    def get_method(environ: dict) -> str:
        """
        Get the HTTP method from WSGI environ.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            HTTP method string
        """
        return environ.get('REQUEST_METHOD', 'GET')
    
    @staticmethod
    def get_headers(environ: dict) -> Dict[str, str]:
        """
        Extract HTTP headers from WSGI environ.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            Dictionary of headers
        """
        headers = {}
        for key, value in environ.items():
            if key.startswith('HTTP_'):
                # Convert HTTP_HEADER_NAME to Header-Name
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        
        # Add some special headers
        if 'CONTENT_TYPE' in environ:
            headers['Content-Type'] = environ['CONTENT_TYPE']
        if 'CONTENT_LENGTH' in environ:
            headers['Content-Length'] = environ['CONTENT_LENGTH']
        
        return headers
    
    @staticmethod
    def get_client_ip(environ: dict) -> str:
        """
        Get client IP address from WSGI environ.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            Client IP address
        """
        # Check for forwarded IP
        forwarded_for = environ.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # Check for real IP
        real_ip = environ.get('HTTP_X_REAL_IP')
        if real_ip:
            return real_ip
        
        # Fall back to remote address
        return environ.get('REMOTE_ADDR', 'unknown')
    
    @staticmethod
    def get_user_agent(environ: dict) -> str:
        """
        Get user agent from WSGI environ.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            User agent string
        """
        return environ.get('HTTP_USER_AGENT', 'unknown')
    
    @staticmethod
    def get_referer(environ: dict) -> Optional[str]:
        """
        Get referer from WSGI environ.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            Referer URL or None
        """
        return environ.get('HTTP_REFERER')
    
    @staticmethod
    def parse_content_type(environ: dict) -> Dict[str, str]:
        """
        Parse content type header from WSGI environ.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            Dictionary with content type info
        """
        content_type = environ.get('CONTENT_TYPE', '')
        
        if not content_type:
            return {'type': '', 'charset': ''}
        
        # Split type and charset
        parts = [part.strip() for part in content_type.split(';')]
        result = {'type': parts[0]}
        
        for part in parts[1:]:
            if part.startswith('charset='):
                result['charset'] = part[8:].strip('"')
        
        return result
    
    @staticmethod
    def is_json_request(environ: dict) -> bool:
        """
        Check if request is JSON.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            True if request content type is JSON
        """
        content_type_info = WSGIHelpers.parse_content_type(environ)
        return content_type_info.get('type', '').startswith('application/json')
    
    @staticmethod
    def is_ajax_request(environ: dict) -> bool:
        """
        Check if request is AJAX.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            True if request is AJAX
        """
        return environ.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
    
    @staticmethod
    def get_request_info(environ: dict) -> Dict[str, Any]:
        """
        Get comprehensive request information.
        
        Args:
            environ: WSGI environment dictionary
            
        Returns:
            Dictionary with request information
        """
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
    """Request object for easier access to request data."""
    
    def __init__(self, environ: dict):
        """
        Initialize request object.
        
        Args:
            environ: WSGI environment dictionary
        """
        self.environ = environ
        self._body = None
        self._params = None
        self._headers = None
        self._json = None
    
    @property
    def method(self) -> str:
        """Get HTTP method."""
        return WSGIHelpers.get_method(self.environ)
    
    @property
    def path(self) -> str:
        """Get request path."""
        return WSGIHelpers.get_path_info(self.environ)
    
    @property
    def params(self) -> Dict[str, str]:
        """Get query parameters."""
        if self._params is None:
            self._params = WSGIHelpers.get_params(self.environ)
        return self._params
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get request headers."""
        if self._headers is None:
            self._headers = WSGIHelpers.get_headers(self.environ)
        return self._headers
    
    @property
    def body(self) -> Optional[Dict[str, Any]]:
        """Get parsed JSON body."""
        if self._json is None:
            self._json = WSGIHelpers.get_body(self.environ)
        return self._json
    
    @property
    def client_ip(self) -> str:
        """Get client IP address."""
        return WSGIHelpers.get_client_ip(self.environ)
    
    @property
    def user_agent(self) -> str:
        """Get user agent."""
        return WSGIHelpers.get_user_agent(self.environ)
    
    def get_param(self, name: str, default: Any = None) -> Any:
        """Get a specific query parameter."""
        return self.params.get(name, default)
    
    def get_header(self, name: str, default: Any = None) -> Any:
        """Get a specific header."""
        return self.headers.get(name, default)
    
    def get_body_field(self, name: str, default: Any = None) -> Any:
        """Get a specific field from JSON body."""
        if self.body:
            return self.body.get(name, default)
        return default
    
    def is_method(self, method: str) -> bool:
        """Check if request method matches."""
        return self.method.upper() == method.upper()
    
    def is_get(self) -> bool:
        """Check if request is GET."""
        return self.is_method('GET')
    
    def is_post(self) -> bool:
        """Check if request is POST."""
        return self.is_method('POST')
    
    def is_put(self) -> bool:
        """Check if request is PUT."""
        return self.is_method('PUT')
    
    def is_delete(self) -> bool:
        """Check if request is DELETE."""
        return self.is_method('DELETE')
    
    def is_ajax(self) -> bool:
        """Check if request is AJAX."""
        return WSGIHelpers.is_ajax_request(self.environ)
    
    def is_json(self) -> bool:
        """Check if request is JSON."""
        return WSGIHelpers.is_json_request(self.environ)
