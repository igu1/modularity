"""API routes configuration for base module."""


def api_routes(module):
    """
    Define API routes for base module.
    
    Args:
        module: Base module instance
        
    Returns:
        List of route tuples (pattern, method, handler)
    """
    views = module.api_views
    
    return [
        ('/api/health', 'GET', views.health_api),
        ('/api/status', 'GET', views.status_api),
    ]
