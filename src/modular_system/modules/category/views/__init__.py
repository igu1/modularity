import json
from ..models.category import CategoryModel

class APIViews:
    def __init__(self, module):
        self.module = module

    def list_api(self, environ, start_response, module_instance):
        service = self.module.services['category_service']
        categories = service.get_all()
        data = {'success': True, 'data': [c.to_dict() for c in categories]}
        body = json.dumps(data).encode('utf-8')
        start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
        return [body]

    def create_api(self, environ, start_response, module_instance):
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        data = json.loads(environ['wsgi.input'].read(content_length))
        category = CategoryModel.from_dict(data)
        cid = self.module.services['category_service'].create(category)
        body = json.dumps({'success': True, 'id': cid}).encode('utf-8')
        start_response('201 Created', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
        return [body]
