import pytest
import os
import tempfile
import json
import io
from modular_system.core.application import ModularSystem
from modular_system.database.connection import init_db, get_engine
from sqlalchemy import text

@pytest.fixture
def app():
    # Use a temporary file for the database
    db_fd, db_path = tempfile.mkstemp()
    db_url = f"sqlite:///{db_path}"
    
    config = {
        'database': {'url': db_url}
    }
    
    # Initialize system
    system = ModularSystem(config)
    
    # Initialize DB and tables
    init_db(db_url)
    
    # Load core modules
    from modular_system.modules import modules as available_modules
    system.registry.set_available_modules(available_modules)
    
    if not system.load_module('base'):
        raise RuntimeError("Failed to load 'base' module")
    if not system.load_module('product'):
        raise RuntimeError("Failed to load 'product' module")
    
    print(f"Available modules: {system.registry.list_available_modules()}")
    print(f"Loaded modules: {system.registry.list_loaded_modules()}")
    print(f"Registered routes: {[r[0] for r in system.registry.get_routes()]}")
    
    yield system
    
    # Cleanup
    os.close(db_fd)
    if os.path.exists(db_path):
        os.unlink(db_path)

@pytest.fixture
def client(app):
    class TestClient:
        def __init__(self, app):
            self.app = app

        def _request(self, method, path, data=None, headers=None):
            headers = headers or {}
            environ = {
                'REQUEST_METHOD': method,
                'PATH_INFO': path,
                'HTTP_HOST': 'localhost',
                'wsgi.input': io.BytesIO(b""),
                'CONTENT_LENGTH': '0'
            }
            
            # Add headers to environ
            for k, v in headers.items():
                env_key = f"HTTP_{k.upper().replace('-', '_')}"
                environ[env_key] = v
            
            if data:
                body = json.dumps(data).encode('utf-8')
                environ['wsgi.input'] = io.BytesIO(body)
                environ['CONTENT_LENGTH'] = str(len(body))
                environ['CONTENT_TYPE'] = 'application/json'

            response_status = []
            response_headers = []

            def start_response(status, headers):
                response_status.append(status)
                response_headers.extend(headers)

            response_body = self.app.request_handler(environ, start_response)
            
            # Extract status code
            status_code = int(response_status[0].split()[0])
            
            # Combine body
            body_content = b"".join(response_body).decode('utf-8')
            try:
                json_data = json.loads(body_content)
            except:
                json_data = body_content
                
            return status_code, json_data, response_headers

        def get(self, path, headers=None):
            return self._request('GET', path, headers=headers)

        def post(self, path, data=None, headers=None):
            return self._request('POST', path, data=data, headers=headers)

        def put(self, path, data=None, headers=None):
            return self._request('PUT', path, data=data, headers=headers)

        def delete(self, path, headers=None):
            return self._request('DELETE', path, headers=headers)

    return TestClient(app)
