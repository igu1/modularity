from typing import Any
class WebViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            service = self.module.services['product_service']
            products = service.get_all()
            
            body = self.module.env.render_template('product', 'list.html', products=products)
            response_body = body.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("product", f"Error in list view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]

    def create_view(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            if environ['REQUEST_METHOD'] == 'POST':
                content_length = int(environ.get('CONTENT_LENGTH', 0))
                post_data = environ['wsgi.input'].read(content_length).decode('utf-8')
                from urllib.parse import parse_qs
                params = parse_qs(post_data)
                
                from ..models.product import ProductModel
                product = ProductModel(
                    name=params.get('name', [''])[0],
                    description=params.get('description', [''])[0],
                    is_active=True
                )
                
                service = self.module.services['product_service']
                service.create(product)
                
                start_response('303 See Other', [('Location', '/web/product')])
                return [b""]

            body = self.module.env.render_template('product', 'create.html')
            response_body = body.encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html'),
                ('Content-Length', str(len(response_body)))
            ])
            return [response_body]
        except Exception as e:
            self.logger.log("product", f"Error in create view: {e}", "error")
            error_body = f"Error: {str(e)}".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/plain'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
