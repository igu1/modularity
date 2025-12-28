from .api import api_routes

def get_routes(module):
    return api_routes(module)

__all__ = ['get_routes', 'api_routes']
