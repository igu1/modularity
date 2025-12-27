"""Web routes configuration for base module."""


def web_routes(module):
    """
    Define web routes for base module.
    
    Args:
        module: Base module instance
        
    Returns:
        List of route tuples (pattern, method, handler)
    """
    views = module.web_views
    
    return [
        ('/', 'GET', views.home_view),
        ('/health', 'GET', views.health_view),
        ('/status', 'GET', views.health_view),  # Reuse health view for status
    ]
