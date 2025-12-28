import json
from datetime import datetime

class WebViews:
    def __init__(self, mod): self.mod = mod

    def _resp(self, body, start, status='200 OK', content_type='text/html'):
        if isinstance(body, (dict, list)):
            body = json.dumps(body).encode()
            content_type = 'application/json'
        elif isinstance(body, str):
            body = body.encode()
        start(status, [('Content-Type', content_type), ('Content-Length', str(len(body)))])
        return [body]

    def home_view(self, env, start, mod):
        body = self.mod.env.render_template('base', 'home.html')
        return self._resp(body, start)

    def health_view(self, env, start, mod):
        return self._resp({"status": "healthy", "ts": str(datetime.now())}, start)
