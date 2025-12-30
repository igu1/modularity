import json
from ..models.cart import CartModel

class APIViews:
    def __init__(self, module):
        self.module = module

    def list_api(self, environ, start_response, module_instance):
        service = self.module.services['cart_service']
        items = service.get_all()
        data = {'success': True, 'data': [i.to_dict() for i in items]}
        body = json.dumps(data).encode('utf-8')
        start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
        return [body]

    def create_api(self, environ, start_response, module_instance):
        content_length = int(environ.get('CONTENT_LENGTH', 0))
        data = json.loads(environ['wsgi.input'].read(content_length))
        cart_item = CartModel.from_dict(data)
        cart_id = self.module.services['cart_service'].create(cart_item)
        body = json.dumps({'success': True, 'id': cart_id}).encode('utf-8')
        start_response('201 Created', [('Content-Type', 'application/json'), ('Content-Length', str(len(body)))])
        return [body]
