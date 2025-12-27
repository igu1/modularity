                                               


def api_routes(module):
\
\
\
\
\
\
\
\
       
    views = module.api_views
    
    return [
        ('/api/health', 'GET', views.health_api),
        ('/api/status', 'GET', views.status_api),
    ]
