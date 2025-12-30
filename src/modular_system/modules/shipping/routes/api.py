def api_routes(module):
    routes = [
        ('/api/shipping/methods', 'GET', module.api_views.methods_api),
        ('/api/shipping/track', 'POST', module.api_views.update_tracking_api),
    ]
    return routes
