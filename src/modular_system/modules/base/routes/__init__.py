from .web import web_routes
from .api import api_routes
def get_routes(module):
    routes = []
    routes.extend(web_routes(module))
    routes.extend(api_routes(module))
    return routes
__all__ = ['get_routes', 'web_routes', 'api_routes']
