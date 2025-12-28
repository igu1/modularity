import json
from urllib.parse import parse_qs
from typing import Dict, Any, Optional, Union, List

class WSGI:
    @staticmethod
    def resp(start, data, code=200, ctype="application/json", headers=None):
        if isinstance(data, (dict, list)):
            body = json.dumps(data, default=str).encode()
            if ctype == "application/json": ctype += "; charset=utf-8"
        else: body = str(data).encode()
        h = [('Content-Type', ctype), ('Content-Length', str(len(body))), ('Access-Control-Allow-Origin', '*')]
        if headers: h.extend(headers)
        start(f"{code} { {200:'OK',201:'Created',400:'Bad Request',401:'Unauthorized',403:'Forbidden',404:'Not Found',500:'Error'}.get(code, 'OK') }", h)
        return [body]

    @staticmethod
    def get_body(env: dict) -> Optional[Dict]:
        try:
            len_ = int(env.get("CONTENT_LENGTH", 0))
            return json.loads(env["wsgi.input"].read(len_).decode()) if len_ > 0 else {}
        except: return None

    @staticmethod
    def get_params(env: dict) -> Dict:
        return {k: v[0] if len(v) == 1 else v for k, v in parse_qs(env.get("QUERY_STRING", "")).items()}

class Request:
    def __init__(self, env: dict):
        self.env = env
        self.method = env.get('REQUEST_METHOD', 'GET')
        self.path = env.get('PATH_INFO', '/')
        self.params = WSGI.get_params(env)
        self.headers = {k[5:].replace('_', '-').title(): v for k, v in env.items() if k.startswith('HTTP_')}
        self.body = WSGI.get_body(env)
