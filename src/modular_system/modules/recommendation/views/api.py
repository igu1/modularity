from typing import Any
import json
class APIViews:
    def __init__(self, module):
        self.module = module
        self.logger = module.logger
    def list_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            service = self.module.services['recommendation_service']
            items = service.get_all()
            data = {
                'success': True,
                'module': 'recommendation',
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
            self.logger.log("recommendation", f"Error in list API: {e}", "error")
            error_data = {'success': False, 'error': str(e)}
            error_body = json.dumps(error_data).encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'application/json'),
                ('Content-Length', str(len(error_body)))
            ])
            return [error_body]
    def recommendations_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            params = environ.get('ROUTE_PARAMS', {})
            product_id = params.get('id')
            service = self.module.services['recommendation_service']
            recs = service.get_recommendations(product_id)
            data = {'success': True, 'product_id': product_id, 'recommendations': recs}
            response_body = json.dumps(data).encode('utf-8')
            start_response('200 OK', [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))])
            return [response_body]
        except Exception as e:
            return [json.dumps({'success': False, 'error': str(e)}).encode('utf-8')]

    def add_recommendation_api(self, environ: dict, start_response: Any, module_instance: Any):
        try:
            content_length = int(environ.get('CONTENT_LENGTH', 0))
            data = json.loads(environ['wsgi.input'].read(content_length))
            service = self.module.services['recommendation_service']
            success = service.add_recommendation(
                data.get('product_id'),
                data.get('recommended_id'),
                data.get('rec_type', 'related'),
                data.get('score', 0)
            )
            res = {'success': success}
            response_body = json.dumps(res).encode('utf-8')
            start_response('201 Created' if success else '400 Bad Request', [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))])
            return [response_body]
        except Exception as e:
            return [json.dumps({'success': False, 'error': str(e)}).encode('utf-8')]
