def web_routes(module):
    views = module.web_views
    return [
        ('/', 'GET', views.home_view),
        ('/health', 'GET', views.health_view),
        ('/status', 'GET', views.health_view),                                
    ]
