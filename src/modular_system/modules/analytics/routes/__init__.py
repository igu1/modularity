from .api import api_routes

def get_routes(mod):
    return api_routes(mod) 

__all__ = ['get_routes']
