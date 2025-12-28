def get_routes(module):
    from .api import get_routes as get_api_routes
    return get_api_routes(module)

__all__ = ['get_routes']
