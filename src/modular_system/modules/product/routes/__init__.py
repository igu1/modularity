from .api import api_routes
from .web import web_routes

def get_routes(mod):
    return api_routes(mod) + web_routes(mod)

__all__ = ['get_routes']
